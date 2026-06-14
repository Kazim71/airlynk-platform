"""
AirLynk — Health check endpoints.

``GET /health``  — deep health check (PostgreSQL, Redis, RabbitMQ)
``GET /ready``   — readiness probe for container orchestration

See API_SPEC.md §5, OBSERVABILITY_PLAN.md §8, SERVICE_TEMPLATE.md §9.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy import text

from backend.shared.cache.redis_client import redis_health_check
from backend.shared.database.session import get_engine
from backend.shared.messaging.rabbitmq import rabbitmq_health_check
from backend.shared.schemas.responses import HealthStatus, SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=SuccessResponse[HealthStatus],
    summary="Service health check",
    description="Checks connectivity to PostgreSQL, Redis, and RabbitMQ.",
)
async def health_check() -> SuccessResponse[HealthStatus]:
    """Deep health check — verifies all infrastructure dependencies."""
    pg_ok = await _check_postgres()
    redis_ok = await redis_health_check()
    rmq_ok = await rabbitmq_health_check()

    status = "healthy" if all([pg_ok, redis_ok, rmq_ok]) else "degraded"

    health = HealthStatus(
        status=status,
        postgres=pg_ok,
        redis=redis_ok,
        rabbitmq=rmq_ok,
    )
    return SuccessResponse(
        message=f"Service is {status}",
        data=health,
    )


@router.get(
    "/ready",
    response_model=SuccessResponse[None],
    summary="Readiness probe",
    description="Lightweight readiness check for container orchestration.",
)
async def readiness_probe() -> SuccessResponse[None]:
    """Readiness probe — returns 200 if the service can accept traffic."""
    return SuccessResponse(message="Service is ready")


async def _check_postgres() -> bool:
    """Execute a lightweight query to verify PostgreSQL connectivity."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.warning("PostgreSQL health check failed")
        return False
