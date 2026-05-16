"""
predict.py — The main prediction endpoint.

Flow:
  1. Receive uploaded image file (multipart/form-data)
  2. Validate file type and size
  3. Preprocess image (resize, normalize)
  4. Run inference → prediction + confidence
  5. Generate Grad-CAM heatmap
  6. Upload image + heatmap to Supabase Storage
  7. Save prediction record to Supabase PostgreSQL
  8. Return full prediction response to frontend
"""

import uuid
import time
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.schemas.prediction import PredictionResponse
from app.services.ml_service import MLService
from app.services.gradcam_service import GradCAMService
from app.services.storage_service import StorageService
from app.core.config import settings
from app.utils.image_utils import validate_image, save_temp_image, cleanup_temp_file

logger = logging.getLogger(__name__)
router = APIRouter()

# Allowed image types
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 10


@router.post("", response_model=PredictionResponse)
async def predict_pneumonia(
    request: Request,
    file: UploadFile = File(..., description="Chest X-ray image (JPEG, PNG, WebP)"),
) -> PredictionResponse:
    """
    Upload a chest X-ray image and receive a pneumonia prediction.
    
    Returns:
    - **prediction**: PNEUMONIA or NORMAL
    - **confidence**: Model confidence score (0.0–1.0)  
    - **image_url**: CDN URL of uploaded X-ray
    - **heatmap_url**: CDN URL of Grad-CAM visualization
    """
    start_time = time.time()
    prediction_id = str(uuid.uuid4())
    temp_path = None
    
    try:
        # ── Step 1: Validate file ──────────────────────────────
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{file.content_type}' not supported. "
                       f"Accepted: JPEG, PNG, WebP",
            )
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Check file size
        file_size_mb = len(file_bytes) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {file_size_mb:.1f}MB exceeds {MAX_FILE_SIZE_MB}MB limit",
            )
        
        # Validate it's actually an image
        validate_image(file_bytes)
        
        # ── Step 2: Save temp file ─────────────────────────────
        temp_path = save_temp_image(file_bytes, prediction_id)
        
        # ── Step 3: Run ML inference ───────────────────────────
        ml_service: MLService = request.app.state.ml_service
        prediction_result = ml_service.predict(file_bytes)
        
        prediction_label = prediction_result["label"]        # "PNEUMONIA" or "NORMAL"
        confidence = prediction_result["confidence"]         # float 0.0–1.0
        
        # ── Step 4: Generate Grad-CAM heatmap ─────────────────
        gradcam_service = GradCAMService(ml_service.model)
        heatmap_bytes = gradcam_service.generate_heatmap(
            file_bytes,
            target_size=(settings.model_input_size, settings.model_input_size)
        )
        
        # ── Step 5: Upload to Supabase Storage ────────────────
        storage_service = StorageService()
        
        image_url = await storage_service.upload_image(
            file_bytes=file_bytes,
            filename=f"{prediction_id}_xray.jpg",
            content_type="image/jpeg",
        )
        
        heatmap_url = await storage_service.upload_image(
            file_bytes=heatmap_bytes,
            filename=f"{prediction_id}_heatmap.jpg",
            content_type="image/jpeg",
        )
        
        # ── Step 6: Save to database ───────────────────────────
        processing_time = (time.time() - start_time) * 1000  # ms
        
        await storage_service.save_prediction(
            prediction_id=prediction_id,
            prediction=prediction_label,
            confidence=confidence,
            image_url=image_url,
            heatmap_url=heatmap_url,
            processing_time_ms=processing_time,
        )
        
        # ── Step 7: Determine severity label ───────────────────
        # Severity helps doctors quickly triage results
        if prediction_label == "PNEUMONIA":
            if confidence >= 0.85:
                severity = "High"
            elif confidence >= 0.65:
                severity = "Medium"
            else:
                severity = "Low"
        else:
            severity = "Normal"
        
        logger.info(
            f"Prediction complete | ID={prediction_id} | "
            f"Result={prediction_label} | Confidence={confidence:.3f} | "
            f"Time={processing_time:.1f}ms"
        )
        
        return PredictionResponse(
            id=prediction_id,
            prediction=prediction_label,
            confidence=round(confidence, 4),
            confidence_percentage=round(confidence * 100, 2),
            severity=severity,
            image_url=image_url,
            heatmap_url=heatmap_url,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.utcnow(),
            model_version="v1.0",
        )
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    
    except Exception as e:
        logger.error(f"Prediction failed for ID={prediction_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )
    
    finally:
        # Always clean up temp files
        if temp_path:
            cleanup_temp_file(temp_path)


@router.get("/test", tags=["Predictions"])
async def test_model(request: Request):
    """Quick model sanity check — returns dummy inference time."""
    ml_service: MLService = request.app.state.ml_service
    return {
        "model_loaded": ml_service.is_loaded,
        "input_shape": str(ml_service.model.input_shape) if ml_service.is_loaded else None,
    }