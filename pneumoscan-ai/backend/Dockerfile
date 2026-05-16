# Use official Python slim image
# slim = smaller image without dev tools (saves ~200MB)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed by OpenCV and TensorFlow
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# This layer is cached separately — if requirements.txt doesn't change,
# Docker skips this expensive step on rebuilds
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create directories
RUN mkdir -p ml_models uploads

# The .h5 model will be copied to the container separately,
# or pulled from a mounted volume on Render.

# Expose port
EXPOSE 8000

# Health check — Render uses this to verify the app is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/api/v1/health || exit 1

# Start command
# - gunicorn: production WSGI server (more robust than uvicorn alone)
# - uvicorn.workers.UvicornWorker: async worker compatible with FastAPI
# - --workers 1: single worker because TensorFlow is not fork-safe with multiple workers
#   (for multi-worker, use TF Serving instead)
CMD ["gunicorn", "app.main:app", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--workers", "1", \
    "--bind", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]