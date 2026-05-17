"""
main.py — FastAPI application factory.

This file:
  1. Creates the FastAPI app instance
  2. Configures middleware (CORS, logging)
  3. Loads the ML model at startup (not per-request — critical for performance)
  4. Mounts all API routers
  5. Adds global exception handlers
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.services.ml_service import MLService

# ── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── ML Service singleton ───────────────────────────────────────
# This is the global model instance, loaded once at startup.
# We store it here so all request handlers share the same loaded model.
ml_service = MLService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — code here runs at startup and shutdown.
    
    Why load the model here instead of per-request?
      Loading a .h5 Keras model takes 2–10 seconds and uses significant RAM.
      Loading it once at startup means every request gets sub-100ms inference.
    """
    # ── STARTUP ───────────────────────────────────────────────
    logger.info("🚀 PneumoScan AI starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Model path: {settings.model_path}")
    
    try:
        ml_service.load_model()
        logger.info("✅ ML model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        raise  # Don't start the server if the model can't load
    
    # Store ml_service on app.state so endpoints can access it
    app.state.ml_service = ml_service
    
    logger.info("✅ PneumoScan AI is ready!")
    
    yield  # ← App runs here
    
    # ── SHUTDOWN ──────────────────────────────────────────────
    logger.info("🛑 PneumoScan AI shutting down...")
    ml_service.cleanup()


# ── Application factory ───────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
## PneumoScan AI — Chest X-Ray Pneumonia Detection API

Upload a chest X-ray image and receive:
- **Binary prediction**: NORMAL or PNEUMONIA
- **Confidence score**: Model certainty (0–100%)  
- **Grad-CAM heatmap**: Visual explanation of the prediction
- **Prediction history**: Stored in Supabase PostgreSQL

### Authentication
Currently open. JWT authentication will be added in v2.

### Rate Limits
- 60 predictions per minute per IP (production)
        """,
        lifespan=lifespan,
        # Disable docs in production for security
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # ── Middleware ─────────────────────────────────────────────
    
    # CORS — allows your Next.js frontend to call this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # GZip — compresses responses > 1KB (saves bandwidth for heatmap URLs)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Request timing middleware ──────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Adds X-Process-Time header to every response for debugging."""
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # milliseconds
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response

    # ── Global exception handlers ──────────────────────────────
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation error", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again.",
            },
        )

    # ── Root endpoint ──────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "model_version": settings.model_version,
            "status": "running",
            "docs": "/docs",
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ── Mount API routes ───────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the app instance
app = create_app()


# ── Entry point for local development ─────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # Auto-reload on file changes in dev
        log_level="info",
    )
