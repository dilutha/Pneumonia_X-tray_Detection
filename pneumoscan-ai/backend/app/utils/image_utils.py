"""
image_utils.py — Image validation and preprocessing helpers.

Why a separate utils module?
  These functions are used by both ml_service.py and gradcam_service.py.
  Centralizing them avoids duplication and makes testing easier.
"""

import io
import uuid
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Temp upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_image(file_bytes: bytes) -> None:
    """
    Verifies that file_bytes is a valid, openable image.
    Raises ValueError if it's corrupted or not an image.
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()  # Checks for corruption without fully decoding
    except (UnidentifiedImageError, Exception) as e:
        raise ValueError(f"Invalid or corrupted image file: {e}")


def preprocess_image(
    file_bytes: bytes,
    target_size: Tuple[int, int] = (150,150),
    normalize: bool = True,
) -> np.ndarray:
    """
    Converts raw image bytes into a preprocessed numpy array
    ready for CNN inference.

    Steps:
      1. Open image with PIL
      2. Convert to RGB (handles grayscale X-rays — some are single-channel)
      3. Resize to model's expected input size
      4. Convert to float32 numpy array
      5. Normalize pixel values to [0, 1]
      6. Add batch dimension: shape (1, H, W, 3)
    """
    # Load image
    img = Image.open(io.BytesIO(file_bytes))
    
    # Convert to RGB
    # X-rays are often grayscale (L mode). CNNs trained on ImageNet expect 3 channels.
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Resize — LANCZOS is the highest quality downsampling filter
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    img_array = np.array(img, dtype=np.float32)
    
    # Normalize: scale pixel values from [0, 255] to [0, 1]
    # Why normalize? Neural networks train and infer more stably with small values.
    if normalize:
        img_array = img_array / 255.0
    
    # Add batch dimension: (H, W, 3) → (1, H, W, 3)
    # TensorFlow expects batches even for single images
    img_array = np.expand_dims(img_array, axis=0)
    
    logger.debug(f"Preprocessed image shape: {img_array.shape}, dtype: {img_array.dtype}")
    return img_array


def bytes_to_pil(file_bytes: bytes) -> Image.Image:
    """Converts raw bytes to a PIL Image object."""
    return Image.open(io.BytesIO(file_bytes)).convert("RGB")


def pil_to_bytes(img: Image.Image, format: str = "JPEG", quality: int = 90) -> bytes:
    """Converts a PIL Image object to bytes."""
    buffer = io.BytesIO()
    img.save(buffer, format=format, quality=quality)
    return buffer.getvalue()


def save_temp_image(file_bytes: bytes, prediction_id: str) -> Path:
    """Saves image bytes to a temp file. Returns the file path."""
    temp_path = UPLOAD_DIR / f"{prediction_id}_temp.jpg"
    temp_path.write_bytes(file_bytes)
    return temp_path


def cleanup_temp_file(path: Path) -> None:
    """Deletes a temp file, silently ignoring errors."""
    try:
        path.unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"Could not delete temp file {path}: {e}")