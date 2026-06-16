"""
AirLynk — FastAPI Application Factory.

This is the single entry-point for the API service.  It wires together:
  - Configuration (Pydantic Settings)
  - Lifespan (startup / shutdown for DB, Redis, RabbitMQ)
  - Middleware chain (Correlation ID → Security Headers → Prometheus)
  - Exception handlers
  - Route registration
  - CORS
  - OpenTelemetry instrumentation
  - OpenAPI metadata

Run with:
    uvicorn backend.main:app --reload
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.shared.cache.redis_client import close_redis, init_redis
from backend.shared.config.settings import get_settings
from backend.shared.database.session import close_db, init_db
from backend.shared.exceptions.handlers import register_exception_handlers
from backend.shared.logging.logger import setup_logging
from backend.shared.messaging.rabbitmq import close_rabbitmq, init_rabbitmq
from backend.shared.middleware.correlation import CorrelationIdMiddleware
from backend.shared.middleware.security_headers import SecurityHeadersMiddleware
from backend.shared.observability.metrics import PrometheusMiddleware
from backend.shared.observability.tracing import setup_tracing, shutdown_tracing

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup & shutdown lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage infrastructure connections across the application lifecycle."""
    settings = get_settings()

    # --- Startup -----------------------------------------------------------
    setup_logging(log_level=settings.app_log_level, service_name=settings.app_name)
    logger.info("Starting AirLynk API", extra={"env": settings.app_env.value})

    await init_db(settings)
    await init_redis(settings)
    await init_rabbitmq(settings)

    logger.info("All infrastructure connections established")

    yield

    # --- Shutdown ----------------------------------------------------------
    logger.info("Shutting down AirLynk API")
    await close_rabbitmq()
    await close_redis()
    await close_db()
    shutdown_tracing()
    logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Build and return the fully-configured FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="AirLynk API",
        description=(
            "Cloud-native secure backend platform — "
            "RESTful APIs with RBAC, audit logging, and distributed observability."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # --- OpenTelemetry -----------------------------------------------------
    setup_tracing(app=application, settings=settings)

    # --- Middleware (order matters: outermost -> innermost) ------------------
    application.add_middleware(PrometheusMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(CorrelationIdMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handlers ------------------------------------------------
    register_exception_handlers(application)

    @application.options("/{full_path:path}", include_in_schema=False)
    async def global_options(full_path: str):
        return {}

    # --- Routes ------------------------------------------------------------
    _register_routes(application)

    return application


def _register_routes(application: FastAPI) -> None:
    """Import and include all API routers."""
    from backend.services.auth.api.routes import router as auth_router
    from backend.services.booking.api.routes import router as booking_router
    from backend.services.dispatch.api.routes import router as dispatch_router
    from backend.services.pricing.api.routes import router as pricing_router
    from backend.services.notification.api.routes import router as notification_router
    from backend.services.notification.events.consumers import init_notification_consumers
    from backend.services.realtime.api.routes import router as realtime_router
    from backend.services.realtime.events.consumers import init_realtime_consumers
    from backend.shared.api.routes.health import router as health_router
    from backend.shared.api.routes.metrics import router as metrics_router

    application.include_router(health_router)
    application.include_router(metrics_router)
    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(booking_router, prefix="/api/v1")
    application.include_router(dispatch_router, prefix="/api/v1")
    application.include_router(pricing_router, prefix="/api/v1")
    application.include_router(notification_router, prefix="/api/v1")
    application.include_router(realtime_router)

    # Initialize event consumers
    init_realtime_consumers()
    init_notification_consumers()


# Module-level app instance — used by Uvicorn
app = create_app()
