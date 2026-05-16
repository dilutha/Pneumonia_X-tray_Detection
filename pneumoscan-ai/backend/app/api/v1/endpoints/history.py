"""
history.py — Fetch past prediction records from Supabase.
"""

from fastapi import APIRouter, Query, HTTPException
from app.schemas.prediction import PredictionHistoryResponse
from app.services.storage_service import StorageService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
) -> PredictionHistoryResponse:
    """
    Returns paginated prediction history sorted by most recent first.
    """
    try:
        storage_service = StorageService()
        result = await storage_service.get_predictions(page=page, page_size=page_size)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch prediction history")


@router.delete("/{prediction_id}", status_code=204)
async def delete_prediction(prediction_id: str) -> None:
    """Delete a specific prediction record and its images."""
    try:
        storage_service = StorageService()
        await storage_service.delete_prediction(prediction_id)
    except Exception as e:
        logger.error(f"Failed to delete prediction {prediction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prediction")