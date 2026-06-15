"""
AirLynk — Structured JSON logging with structlog.

Produces JSON-formatted log lines compliant with OBSERVABILITY_PLAN.md §4:

    Required fields: timestamp, service_name, request_id, log_level, message

Sensitive data filtering:
    Passwords, JWT tokens, refresh tokens, and secrets are NEVER logged
    (OBSERVABILITY_PLAN.md §Sensitive Data Policy).
"""

from __future__ import annotations

import logging
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import structlog
from opentelemetry import trace

from backend.shared.config.settings import get_settings
from backend.shared.middleware.correlation import request_id_ctx

# Fields that must never appear in log output
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "refresh_token",
        "access_token",
        "jwt",
        "authorization",
        "cookie",
    }
)


def _filter_sensitive_data(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Redact values for sensitive keys."""
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def _inject_request_id(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Inject the current request ID from the context var."""
    req_id = request_id_ctx.get("")
    if req_id:
        event_dict["request_id"] = req_id
    return event_dict


def _inject_service_name(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Inject the service name from settings (or default)."""
    event_dict.setdefault("service_name", "airlynk")
    return event_dict


def _inject_trace_context(
    logger: logging.Logger, log_method: str, event_dict: structlog.types.EventDict
) -> structlog.types.EventDict:
    """Inject OTEL trace_id and span_id into structured logs."""
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = trace.format_trace_id(ctx.trace_id)
        event_dict["span_id"] = trace.format_span_id(ctx.span_id)

    # Inject static platform context
    settings = get_settings()
    event_dict["service_name"] = "airlynk-api"
    event_dict["environment"] = settings.ENVIRONMENT  # type: ignore

    return event_dict


def setup_logging(log_level: str = "INFO", service_name: str = "airlynk") -> None:
    """Configure structured JSON logging for the entire application.

    Call once during application startup — before any other module logs.
    """

    def _add_service(
        _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        event_dict.setdefault("service_name", service_name)
        return event_dict

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_service,
        _inject_request_id,
        _inject_trace_context,
        _filter_sensitive_data,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Quiet noisy third-party loggers
    for name in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger for the given module name."""
    return cast("structlog.stdlib.BoundLogger", structlog.get_logger(name))
