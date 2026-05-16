"""
gradcam_service.py — Generates Grad-CAM heatmap visualizations.

Improved Version:
  ✅ Fixed weak/same-image Grad-CAM issue
  ✅ Proper heatmap normalization
  ✅ Better CNN feature weighting
  ✅ Stronger visual contrast
  ✅ Better debugging logs
  ✅ Correct handling for binary classification
  ✅ Stable overlay generation
"""

import logging
from typing import Optional, Tuple

import numpy as np
import cv2

# TensorFlow 2.17 compatibility fix for Python 3.12
try:
    import _distutils_hack.override  # noqa: F401
except Exception:
    pass

import tensorflow as tf
from PIL import Image

from app.utils.image_utils import (
    preprocess_image,
    bytes_to_pil,
    pil_to_bytes,
)

logger = logging.getLogger(__name__)


class GradCAMService:
    """
    Generates Grad-CAM visual explanations for CNN predictions.

    Args:
        model:
            Loaded TensorFlow/Keras model

        last_conv_layer_name:
            Optional manual layer selection.
            If None, automatically finds last Conv2D layer.
    """

    def __init__(
        self,
        model: tf.keras.Model,
        last_conv_layer_name: Optional[str] = None,
    ):
        self.model = model

        self.last_conv_layer_name = (
            last_conv_layer_name
            or self._find_last_conv_layer()
        )

        logger.info(
            f"✅ Grad-CAM initialized using layer: "
            f"{self.last_conv_layer_name}"
        )

    # ============================================================
    # AUTO DETECT LAST CONV LAYER
    # ============================================================

    def _find_last_conv_layer(self) -> str:
        """
        Finds the final convolution layer automatically.

        Grad-CAM works best on the deepest convolution layer
        because it contains high-level semantic features while
        still preserving spatial information.
        """

        for layer in reversed(self.model.layers):

            if isinstance(
                layer,
                (
                    tf.keras.layers.Conv2D,
                    tf.keras.layers.SeparableConv2D,
                    tf.keras.layers.DepthwiseConv2D,
                ),
            ):
                logger.info(
                    f"Detected last conv layer: {layer.name}"
                )
                return layer.name

        raise ValueError(
            "No convolution layer found in model."
        )

    # ============================================================
    # COMPUTE GRAD-CAM HEATMAP
    # ============================================================

    def compute_heatmap(
        self,
        img_array: np.ndarray,
        pred_index: Optional[int] = None,
    ) -> np.ndarray:
        """
        Computes raw Grad-CAM heatmap.

        Args:
            img_array:
                Preprocessed image
                Shape: (1, H, W, 3)

            pred_index:
                Optional class index

        Returns:
            heatmap:
                2D normalized numpy array
        """

        # Feature extractor model
        grad_model = tf.keras.models.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(
                    self.last_conv_layer_name
                ).output,
                self.model.output,
            ],
        )

        # ========================================================
        # FORWARD + GRADIENT PASS
        # ========================================================

        with tf.GradientTape() as tape:

            inputs = tf.cast(img_array, tf.float32)

            conv_outputs, predictions = grad_model(inputs)

            logger.debug(
                f"Predictions: {predictions.numpy()}"
            )

            # Binary classification
            if predictions.shape[-1] == 1:

                probability = predictions[:, 0]

                if pred_index is None:
                    pred_index = 0

                class_score = probability

            # Multi-class classification
            else:

                if pred_index is None:
                    pred_index = tf.argmax(predictions[0])

                class_score = predictions[:, pred_index]

        # ========================================================
        # COMPUTE GRADIENTS
        # ========================================================

        grads = tape.gradient(
            class_score,
            conv_outputs,
        )

        if grads is None:
            raise ValueError(
                "Failed to compute gradients for Grad-CAM."
            )

        # ========================================================
        # GLOBAL AVERAGE POOLING
        # ========================================================

        pooled_grads = tf.reduce_mean(
            grads,
            axis=(0, 1, 2),
        )

        # Remove batch dimension
        conv_outputs = conv_outputs[0]

        logger.debug(
            f"Conv output shape: {conv_outputs.shape}"
        )

        logger.debug(
            f"Pooled grads shape: {pooled_grads.shape}"
        )

        # ========================================================
        # WEIGHT FEATURE MAPS
        # ========================================================

        heatmap = tf.reduce_sum(
            conv_outputs * pooled_grads,
            axis=-1,
        )

        # ========================================================
        # RELU ACTIVATION
        # ========================================================

        heatmap = tf.maximum(heatmap, 0)

        # ========================================================
        # NORMALIZATION
        # ========================================================

        max_val = tf.reduce_max(heatmap)

        if max_val == 0:
            logger.warning(
                "Heatmap max value is zero. Returning blank heatmap."
            )

            return np.zeros_like(heatmap.numpy())

        heatmap /= max_val

        heatmap_np = heatmap.numpy()

        logger.debug(
            f"Heatmap min: {heatmap_np.min():.4f} | "
            f"max: {heatmap_np.max():.4f}"
        )

        return heatmap_np

    # ============================================================
    # GENERATE OVERLAY IMAGE
    # ============================================================

    def generate_heatmap(
        self,
        file_bytes: bytes,
        target_size: Tuple[int, int] = (150, 150),
        alpha: float = 0.55,
        colormap: int = cv2.COLORMAP_JET,
    ) -> bytes:
        """
        Generates heatmap overlay image.

        Args:
            file_bytes:
                Original image bytes

            target_size:
                MUST match model training input size

            alpha:
                Heatmap opacity

            colormap:
                OpenCV colormap

        Returns:
            JPEG image bytes
        """

        try:

            logger.info(
                "Generating Grad-CAM heatmap..."
            )

            # ====================================================
            # PREPROCESS IMAGE
            # ====================================================

            img_array = preprocess_image(
                file_bytes,
                target_size=target_size,
            )

            logger.debug(
                f"Input array shape: {img_array.shape}"
            )

            # ====================================================
            # COMPUTE HEATMAP
            # ====================================================

            heatmap = self.compute_heatmap(img_array)

            # ====================================================
            # LOAD ORIGINAL IMAGE
            # ====================================================

            original_pil = bytes_to_pil(file_bytes)

            original_pil = original_pil.convert("RGB")

            original_pil = original_pil.resize(
                target_size,
                Image.Resampling.LANCZOS,
            )

            original_np = np.array(original_pil)

            # ====================================================
            # RESIZE HEATMAP
            # ====================================================

            heatmap_resized = cv2.resize(
                heatmap,
                (target_size[1], target_size[0]),
                interpolation=cv2.INTER_CUBIC,
            )

            # ====================================================
            # NORMALIZE AFTER RESIZE
            # ====================================================

            heatmap_resized = np.maximum(
                heatmap_resized,
                0,
            )

            heatmap_resized = heatmap_resized / (
                np.max(heatmap_resized) + 1e-8
            )

            # ====================================================
            # CONVERT TO UINT8
            # ====================================================

            heatmap_uint8 = np.uint8(
                255 * heatmap_resized
            )

            # ====================================================
            # APPLY COLORMAP
            # ====================================================

            heatmap_colored = cv2.applyColorMap(
                heatmap_uint8,
                colormap,
            )

            # OpenCV uses BGR
            heatmap_colored = cv2.cvtColor(
                heatmap_colored,
                cv2.COLOR_BGR2RGB,
            )

            # ====================================================
            # BLEND IMAGES
            # ====================================================

            overlay = cv2.addWeighted(
                original_np.astype(np.float32),
                1 - alpha,
                heatmap_colored.astype(np.float32),
                alpha,
                0,
            )

            overlay = np.clip(
                overlay,
                0,
                255,
            ).astype(np.uint8)

            # ====================================================
            # CONVERT TO OUTPUT BYTES
            # ====================================================

            overlay_pil = Image.fromarray(overlay)

            logger.info(
                "✅ Grad-CAM heatmap generated successfully"
            )

            return pil_to_bytes(
                overlay_pil,
                format="JPEG",
                quality=95,
            )

        except Exception as e:

            logger.error(
                f"❌ Grad-CAM generation failed: {e}",
                exc_info=True,
            )

            logger.warning(
                "Returning original image as fallback"
            )

            return file_bytes