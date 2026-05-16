"""
router.py — Aggregates all v1 endpoint routers into one.

Why have a separate router file?
  Clean separation. Adding a new feature (e.g., /auth) means adding
  one line here, not touching main.py.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import predict, history, health

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    predict.router,
    prefix="/predict",
    tags=["Predictions"],
)

api_router.include_router(
    history.router,
    prefix="/history",
    tags=["History"],
)