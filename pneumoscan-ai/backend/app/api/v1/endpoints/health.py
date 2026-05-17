"""
health.py — System health check endpoint.

Used by:
  - Render: to confirm the app is running (uptime monitoring)
  - Frontend: to show API status in the dashboard
  - DevOps: to detect model loading failures
"""

from fastapi import APIRouter, Request
from datetime import datetime
from app.core.config import settings
from app.schemas.prediction import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """
    Returns API health status including whether the ML model is loaded.
    
    This endpoint should NEVER require authentication — monitoring tools
    must be able to reach it freely.
    """
    ml_service = request.app.state.ml_service
    
    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_loaded,
        environment=settings.environment,
        version=settings.model_version,
        timestamp=datetime.utcnow(),
    )
