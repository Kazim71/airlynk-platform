"""
AirLynk — Security headers middleware.

Injects the mandatory response headers from SECURITY.md §4:
  - Strict-Transport-Security
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_SECURITY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add hardened security headers to every response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            # Allow Swagger UI to load by relaxing CSP on /docs and /openapi.json
            if header == "Content-Security-Policy" and request.url.path in [
                "/docs",
                "/openapi.json",
            ]:
                response.headers.setdefault(
                    header,
                    "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: cdn.jsdelivr.net; img-src 'self' data: fastapitiangolo.tiangolo.com;",
                )
            else:
                response.headers.setdefault(header, value)
        return response
