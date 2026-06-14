"""
AirLynk — Centralized exception handling.

Custom exception hierarchy mapped to HTTP status codes as defined in
API_SPEC.md §HTTP Status Standards.

The ``register_exception_handlers`` function wires these into FastAPI so that
unhandled domain exceptions automatically produce the standard error response
format.

Forbidden: silent exceptions, broad exception swallowing, print debugging
(CODING_STANDARDS.md §10).
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class AirLynkError(Exception):
    """Base exception for all AirLynk domain errors."""

    status_code: int = 500
    default_message: str = "Internal server error"

    def __init__(self, message: str | None = None, errors: list[Any] | None = None) -> None:
        self.message = message or self.default_message
        self.errors = errors or []
        super().__init__(self.message)


class NotFoundError(AirLynkError):
    """Resource not found — HTTP 404."""

    status_code = 404
    default_message = "Resource not found"


class AuthenticationError(AirLynkError):
    """Invalid or missing credentials — HTTP 401."""

    status_code = 401
    default_message = "Authentication failed"


class AuthorizationError(AirLynkError):
    """Insufficient permissions — HTTP 403."""

    status_code = 403
    default_message = "Permission denied"


class ValidationError(AirLynkError):
    """Domain-level validation failure — HTTP 422."""

    status_code = 422
    default_message = "Validation error"


class ConflictError(AirLynkError):
    """Duplicate or conflicting state — HTTP 409."""

    status_code = 409
    default_message = "Resource conflict"


class RateLimitError(AirLynkError):
    """Rate limit exceeded — HTTP 429."""

    status_code = 429
    default_message = "Rate limit exceeded"


# ---------------------------------------------------------------------------
# FastAPI exception handler registration
# ---------------------------------------------------------------------------


def _error_body(message: str, errors: list[Any] | None = None) -> dict[str, Any]:
    return {"success": False, "message": message, "errors": errors or []}


def register_exception_handlers(app: FastAPI) -> None:
    """Wire all exception handlers into the FastAPI app."""

    @app.exception_handler(AirLynkError)
    async def _airlynk_error_handler(request: Request, exc: AirLynkError) -> JSONResponse:
        logger.warning(
            "Domain error: %s",
            exc.message,
            extra={"status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.message, exc.errors),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_body("Validation failed", errors),
        )

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("Internal server error"),
        )
