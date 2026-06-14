# ============================================================
# AirLynk API — Multi-stage Dockerfile
# ============================================================
# Base image:  python:3.12-slim  (DOCKER_STRATEGY.md §2)
# Security:    non-root user     (DOCKER_STRATEGY.md §3)
# Strategy:    multi-stage build (DOCKER_STRATEGY.md §9)
# ============================================================

# ---------------------------------------------------------------------------
# Stage 1 — Dependency installation
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# System deps for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install .

# ---------------------------------------------------------------------------
# Stage 2 — Minimal runtime image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL maintainer="AirLynk Engineering"
LABEL description="AirLynk API Service"

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user (DOCKER_STRATEGY.md §3)
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
WORKDIR /app
COPY backend/ ./backend/

# Ensure appuser owns the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose API port (DOCKER_STRATEGY.md §4)
EXPOSE 8000

# Health check (DOCKER_STRATEGY.md §10)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Uvicorn
CMD ["uvicorn", "backend.services.api.app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--loop", "uvloop", "--http", "httptools"]
