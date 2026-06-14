"""
AirLynk — OpenTelemetry distributed tracing bootstrap.

Sets up a TracerProvider with an OTLP exporter and auto-instruments:
  - FastAPI (request spans)
  - SQLAlchemy (DB query spans)
  - Redis (cache operation spans)
  - Celery (task spans — when running in worker context)

See OBSERVABILITY_PLAN.md §5 and SERVICE_TEMPLATE.md §15.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from backend.shared.config.settings import Settings, get_settings

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_tracing(app: FastAPI | None = None, settings: Settings | None = None) -> None:
    """Initialise the OpenTelemetry tracer provider and instrument libraries.

    In development mode a ``ConsoleSpanExporter`` is used alongside the OTLP
    exporter so traces are visible in stdout.
    """
    settings = settings or get_settings()

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": "0.1.0",
            "deployment.environment": settings.app_env.value,
        }
    )

    provider = TracerProvider(resource=resource)

    # OTLP exporter — sends to a collector (Jaeger, Tempo, etc.)
    if settings.otel_enabled:
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.otel_exporter_otlp_endpoint,
                insecure=settings.is_development,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except Exception as e:
            logger.warning("Failed to initialize OTLP exporter", exc_info=e)

        # Console exporter for dev visibility
        if settings.is_development:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # --- Auto-instrument libraries -------------------------------------------
    if app is not None:
        try:
            FastAPIInstrumentor.instrument_app(app)
        except Exception as e:
            logger.warning("FastAPI instrumentation skipped", exc_info=e)

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument()
    except Exception:
        logger.debug("SQLAlchemy instrumentation skipped (engine not ready)")

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
    except Exception:
        logger.debug("Redis instrumentation skipped")

    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument()  # type: ignore[no-untyped-call]
    except Exception:
        logger.debug("Celery instrumentation skipped")

    logger.info("OpenTelemetry tracing initialised", extra={"service": settings.otel_service_name})


def shutdown_tracing() -> None:
    """Flush and shut down the tracer provider."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()
