"""
ml_service.py — Model loading and inference service.

Design decisions:
  - Singleton pattern: model loaded once, reused per request
  - Model stored on app.state (FastAPI's request-scoped state)
  - Warm-up prediction at startup to pre-compile TF graphs
  - Thread-safe: TF inference is inherently thread-safe for read operations
"""

import logging
import time
from typing import Optional, Dict, Any

import numpy as np

# TensorFlow 2.17 still imports distutils. Python 3.12 removed stdlib
# distutils, so we explicitly enable setuptools' compatibility shim first.
try:
    import _distutils_hack.override  # noqa: F401
except Exception:
    pass

import tensorflow as tf

from app.core.config import settings
from app.utils.image_utils import preprocess_image

logger = logging.getLogger(__name__)


class MLService:
    """
    Manages the lifecycle of the TensorFlow/Keras DenseNet121 model.
    
    Usage:
        ml_service = MLService()
        ml_service.load_model()           # Call once at startup
        result = ml_service.predict(img)  # Call per request
    """

    def __init__(self):
        self.model: Optional[tf.keras.Model] = None
        self.is_loaded: bool = False
        self._input_size = (settings.model_input_size, settings.model_input_size)

    def load_model(self) -> None:
        """
        Loads the Keras .h5 model from disk.
        
        Why load at startup?
          A .h5 model file is deserialized (weights parsed, graph compiled).
          This takes 2–15 seconds depending on model size.
          If done per-request, your API has 15-second latency on the first hit.
          Loading once gives ~50–200ms inference per request.
        """
        model_path = settings.resolved_model_path
        logger.info(f"Loading model from: {model_path}")
        start = time.time()
        
        try:
            if not model_path.exists():
                raise FileNotFoundError(str(model_path))

            # Load model with compile=False for pure inference
            # (We don't need optimizer state for predictions)
            self.model = tf.keras.models.load_model(
                model_path,
                compile=False
            )

            self._validate_model_input_shape()
            
            load_time = (time.time() - start) * 1000
            logger.info(f"Model loaded in {load_time:.0f}ms")
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")
            
            # ── Warm-up prediction ─────────────────────────────
            # Run a dummy inference to pre-compile the TF computation graph.
            # First prediction is always slower; this pays the cost at startup.
            logger.info("Running warm-up inference...")
            dummy_input = np.zeros((1, *self._input_size, 3), dtype=np.float32)
            _ = self.model.predict(dummy_input, verbose=0)
            logger.info("Warm-up complete")
            
            self.is_loaded = True
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at '{model_path}'. "
                f"Make sure you've placed your .h5 file in the ml_models/ directory."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def _validate_model_input_shape(self) -> None:
        """Fail fast when MODEL_INPUT_SIZE does not match the saved DenseNet121 model."""
        if self.model is None:
            raise RuntimeError("Model instance is missing after load.")

        input_shape = self.model.input_shape
        if isinstance(input_shape, list):
            input_shape = input_shape[0]

        if len(input_shape) != 4:
            raise ValueError(f"Expected a 4D image model input, got {input_shape}.")

        expected = (settings.model_input_size, settings.model_input_size, 3)
        actual = tuple(input_shape[1:4])
        if None not in actual and actual != expected:
            raise ValueError(
                "Model input shape mismatch. "
                f"Saved model expects {actual}, but settings specify {expected}. "
                "Set MODEL_INPUT_SIZE=224 for the DenseNet121 transfer learning model."
            )

    def predict(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Runs inference on a chest X-ray image.
        
        Args:
            file_bytes: Raw image bytes (JPEG, PNG, WebP)
        
        Returns:
            dict with keys: label, confidence, raw_output
        
        DenseNet121 output interpretation:
          - Our model has 1 output neuron with sigmoid activation
          - Output ∈ [0, 1]
          - Values closer to 1 → PNEUMONIA
          - Values closer to 0 → NORMAL
          - Threshold: 0.5 (configurable via CONFIDENCE_THRESHOLD)
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        # Preprocess
        img_array = preprocess_image(file_bytes, target_size=self._input_size)
        
        # Inference
        start = time.time()
        raw_output = self.model.predict(img_array, verbose=0)
        inference_ms = (time.time() - start) * 1000
        
        logger.debug(f"Raw output: {raw_output} | Inference: {inference_ms:.1f}ms")
        
        # Parse output
        # Handle both binary (1 neuron) and softmax (2 neurons) output shapes
        if raw_output.shape[-1] == 1:
            # Binary sigmoid output — standard for binary classification
            probability = float(raw_output[0][0])
            is_pneumonia = probability >= settings.confidence_threshold
            
            label = "PNEUMONIA" if is_pneumonia else "NORMAL"
            # Confidence is the model's certainty in its prediction
            confidence = probability if is_pneumonia else (1.0 - probability)
            
        elif raw_output.shape[-1] == 2:
            # Softmax output with 2 classes: [P(NORMAL), P(PNEUMONIA)]
            probabilities = raw_output[0]
            label = "PNEUMONIA" if probabilities[1] > probabilities[0] else "NORMAL"
            confidence = float(probabilities[1] if label == "PNEUMONIA" else probabilities[0])
        else:
            raise ValueError(f"Unexpected model output shape: {raw_output.shape}")
        
        return {
            "label": label,
            "confidence": confidence,
            "raw_output": raw_output.tolist(),
            "inference_ms": inference_ms,
        }

    def cleanup(self) -> None:
        """Release model from memory on shutdown."""
        if self.model is not None:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("ML model released from memory")

    def get_model_summary(self) -> str:
        """Returns model architecture summary as string."""
        if not self.is_loaded:
            return "Model not loaded"
        import io
        stream = io.StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + "\n"))
        return stream.getvalue()
