"""Image validation and DenseNet121 preprocessing helpers."""

import io
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError

# TensorFlow 2.17 still imports distutils. Python 3.12 removed stdlib
# distutils, so we explicitly enable setuptools' compatibility shim first.
try:
    import _distutils_hack.override  # noqa: F401
except Exception:
    pass

from tensorflow.keras.applications.densenet import preprocess_input

logger = logging.getLogger(__name__)

# Temp upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_image(file_bytes: bytes) -> None:
    """
    Verifies that file_bytes is a valid, openable image.
    Raises ValueError if it's corrupted or not an image.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()  # Checks for corruption without fully decoding
    except (UnidentifiedImageError, Exception) as e:
        raise ValueError(f"Invalid or corrupted image file: {e}")


def preprocess_image(
    file_bytes: bytes,
    target_size: Tuple[int, int] = (224, 224),
) -> np.ndarray:
    """
    Converts raw image bytes into a preprocessed numpy array
    ready for DenseNet121 inference.

    Steps:
      1. Open image with PIL
      2. Convert to RGB (handles grayscale X-rays — some are single-channel)
      3. Resize to model's expected input size
      4. Convert to float32 numpy array
      5. Apply tf.keras.applications.densenet.preprocess_input
      6. Add batch dimension: shape (1, H, W, 3)
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
    except (UnidentifiedImageError, Exception) as e:
        raise ValueError(f"Invalid or corrupted image file: {e}") from e

    img = img.convert("RGB")
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
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
