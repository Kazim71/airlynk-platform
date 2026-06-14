"""
AirLynk — Correlation / Request ID middleware.

Every request is assigned a unique ``X-Request-ID`` header.  If the client
already provides one it is honoured; otherwise a UUID v4 is generated.

The ID is:
  - propagated to the response headers
  - injected into structlog context for downstream logging
  - used as the OpenTelemetry correlation ID

See OBSERVABILITY_PLAN.md §5 (Correlation IDs).
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

# Module-level context var — accessible from any async context.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request/response cycle."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Honour existing header or generate a new one
        req_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request_id_ctx.set(req_id)

        # Store in request state so dependencies can access it
        request.state.request_id = req_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = req_id
        return response
