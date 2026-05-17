"""
storage_service.py — Handles all Supabase operations.

Two responsibilities:
  1. Storage: Upload X-ray images and heatmaps to Supabase Storage (S3-compatible CDN)
  2. Database: Save/retrieve prediction records from PostgreSQL
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi.concurrency import run_in_threadpool
from supabase import create_client, Client

from app.core.config import settings
from app.schemas.prediction import PredictionHistoryResponse, PredictionHistoryItem

logger = logging.getLogger(__name__)


def classify_severity(prediction: str, confidence: float) -> str:
    """Clinical triage label tuned for better-calibrated DenseNet121 probabilities."""
    if prediction != "PNEUMONIA":
        return "Normal"
    if confidence >= 0.90:
        return "High"
    if confidence >= 0.75:
        return "Medium"
    return "Low"


def get_supabase_client() -> Client:
    """
    Creates a Supabase client using the service role key.
    
    Why service role key (not anon key)?
      The anon key respects RLS policies, which is right for the frontend.
      The service role key bypasses RLS — appropriate for backend server operations
      (we've already validated the request at the FastAPI layer).
    """
    if not settings.supabase_enabled:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY "
            "to enable storage and prediction history."
        )
    return create_client(
        settings.supabase_url.strip().strip('"').strip("'"),
        settings.supabase_service_key.strip().strip('"').strip("'"),
    )


class StorageService:
    """Handles all Supabase Storage and PostgreSQL operations."""

    def __init__(self):
        self.client: Optional[Client] = get_supabase_client() if settings.supabase_enabled else None
        self.bucket = settings.supabase_bucket
        self.table = "predictions"

    @property
    def enabled(self) -> bool:
        return self.client is not None

    async def upload_image(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg",
    ) -> Optional[str]:
        """
        Uploads an image to Supabase Storage and returns the public CDN URL.
        
        Returns None if upload fails (we don't want image upload failure
        to block the prediction response).
        """
        if not self.enabled:
            logger.warning("Supabase storage skipped because Supabase is not configured.")
            return None

        try:
            # Upload to Supabase Storage
            await run_in_threadpool(
                self.client.storage.from_(self.bucket).upload,
                path=filename,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            
            # Get the public URL
            public_url = self.client.storage.from_(self.bucket).get_public_url(filename)
            logger.info(f"Uploaded {filename} → {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload {filename} to Supabase Storage: {e}")
            return None

    async def save_prediction(
        self,
        prediction_id: str,
        prediction: str,
        confidence: float,
        image_url: Optional[str],
        heatmap_url: Optional[str],
        processing_time_ms: float,
        model_version: str = settings.model_version,
    ) -> bool:
        """
        Saves a prediction record to the PostgreSQL predictions table.
        
        Returns True if successful, False otherwise.
        """
        if not self.enabled:
            logger.warning("Prediction persistence skipped because Supabase is not configured.")
            return False

        try:
            severity = classify_severity(prediction, confidence)

            data = {
                "id": prediction_id,
                "prediction": prediction,
                "confidence": round(confidence, 4),
                "confidence_percentage": round(confidence * 100, 2),
                "severity": severity,
                "image_url": image_url,
                "heatmap_url": heatmap_url,
                "processing_time_ms": round(processing_time_ms, 2),
                "model_version": model_version,
            }
            
            await run_in_threadpool(self.client.table(self.table).insert(data).execute)
            logger.info(f"Saved prediction {prediction_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save prediction to database: {e}")
            return False

    async def get_predictions(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> PredictionHistoryResponse:
        """
        Fetches paginated prediction history, newest first.
        """
        offset = (page - 1) * page_size

        if not self.enabled:
            logger.warning("Prediction history requested while Supabase is not configured.")
            return PredictionHistoryResponse(items=[], total=0, page=page, page_size=page_size)
        
        try:
            # Get total count
            count_response = await run_in_threadpool(
                self.client.table(self.table).select("id", count="exact").execute
            )
            total = count_response.count or 0
            
            # Get paginated data
            response = await run_in_threadpool(
                self.client.table(self.table)
                .select("*")
                .order("created_at", desc=True)
                .range(offset, offset + page_size - 1)
                .execute
            )
            
            items = [
                PredictionHistoryItem(
                    id=row["id"],
                    prediction=row["prediction"],
                    confidence=row["confidence"],
                    confidence_percentage=row["confidence_percentage"],
                    severity=row["severity"],
                    image_url=row.get("image_url"),
                    heatmap_url=row.get("heatmap_url"),
                    timestamp=row["created_at"],
                    model_version=row.get("model_version", settings.model_version),
                )
                for row in response.data
            ]
            
            return PredictionHistoryResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch prediction history: {e}")
            return PredictionHistoryResponse(
                items=[], total=0, page=page, page_size=page_size
            )

    async def delete_prediction(self, prediction_id: str) -> bool:
        """Deletes a prediction record and its associated images."""
        if not self.enabled:
            logger.warning("Delete skipped because Supabase is not configured.")
            return False

        try:
            # Get the record first to find image paths
            response = await run_in_threadpool(
                self.client.table(self.table)
                .select("image_url, heatmap_url")
                .eq("id", prediction_id)
                .execute
            )
            
            if response.data:
                record = response.data[0]
                # Extract filenames from URLs and delete from storage
                for url_field in ["image_url", "heatmap_url"]:
                    url = record.get(url_field)
                    if url:
                        # Extract filename from URL
                        filename = url.split("/")[-1]
                        try:
                            await run_in_threadpool(
                                self.client.storage.from_(self.bucket).remove,
                                [filename],
                            )
                        except Exception as e:
                            logger.warning(f"Could not delete image {filename}: {e}")
            
            # Delete database record
            await run_in_threadpool(
                self.client.table(self.table).delete().eq("id", prediction_id).execute
            )
            logger.info(f"Deleted prediction {prediction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete prediction {prediction_id}: {e}")
            return False
