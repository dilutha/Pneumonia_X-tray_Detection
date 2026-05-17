"""
schemas/prediction.py — Pydantic models for request/response validation.

Why Pydantic schemas?
  - FastAPI auto-generates OpenAPI docs from these
  - Validates incoming data types before they reach your business logic
  - Serializes outgoing data (converts Python objects → JSON)
  - Separate from ORM models (separation of concerns)
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


BASE_MODEL_CONFIG = ConfigDict(
    from_attributes=True,
    protected_namespaces=(),
)


class PredictionResponse(BaseModel):
    """
    Returned to the frontend after a successful prediction.
    Every field has a description — these appear in Swagger docs.
    """
    model_config = BASE_MODEL_CONFIG

    id: str = Field(..., description="Unique prediction ID (UUID)")
    prediction: str = Field(..., description="'PNEUMONIA' or 'NORMAL'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence 0.0–1.0")
    confidence_percentage: float = Field(..., description="Confidence × 100 for display")
    severity: str = Field(..., description="'High', 'Medium', or 'Low' risk label")
    image_url: Optional[str] = Field(None, description="Supabase Storage URL of uploaded X-ray")
    heatmap_url: Optional[str] = Field(None, description="Supabase Storage URL of Grad-CAM heatmap")
    processing_time_ms: float = Field(..., description="Inference time in milliseconds")
    timestamp: datetime = Field(..., description="UTC timestamp of prediction")
    model_version: str = Field(default="DenseNet121-v2", description="Which model checkpoint was used")


class PredictionHistoryItem(BaseModel):
    """Single item in the history list."""
    model_config = BASE_MODEL_CONFIG

    id: str
    prediction: str
    confidence: float
    confidence_percentage: float
    severity: str
    image_url: Optional[str]
    heatmap_url: Optional[str]
    timestamp: datetime
    model_version: str


class PredictionHistoryResponse(BaseModel):
    """Paginated list of past predictions."""
    model_config = ConfigDict(protected_namespaces=())

    items: list[PredictionHistoryItem]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Returned by the /health endpoint — used by Render and monitoring tools."""
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    environment: str
    version: str
    timestamp: datetime
