"""
AirLynk — Prometheus metrics.

Exposes custom application metrics aligned with OBSERVABILITY_PLAN.md §3:
  - request count (by method, path, status)
  - request latency histogram
  - active requests gauge
  - error counter

The ``/metrics`` endpoint is served by the ``metrics_endpoint`` function.
"""

from __future__ import annotations

import time

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Dedicated registry — avoids pollution from default process collectors
# in unit tests while still exposing all platform metrics.
REGISTRY = CollectorRegistry()

# --- Application metrics ---------------------------------------------------

REQUEST_COUNT = Counter(
    "airlynk_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "airlynk_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

ACTIVE_REQUESTS = Gauge(
    "airlynk_http_active_requests",
    "Currently active HTTP requests",
    registry=REGISTRY,
)

ERROR_COUNT = Counter(
    "airlynk_http_errors_total",
    "Total HTTP 5xx errors",
    ["method", "path"],
    registry=REGISTRY,
)


# --- Middleware for automatic collection -----------------------------------


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collect request count, latency, and active-requests metrics."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Normalise path to avoid high-cardinality explosion
        path = request.url.path
        method = request.method

        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            ERROR_COUNT.labels(method=method, path=path).inc()
            raise
        finally:
            duration = time.perf_counter() - start
            ACTIVE_REQUESTS.dec()

        REQUEST_COUNT.labels(method=method, path=path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)

        if response.status_code >= 500:
            ERROR_COUNT.labels(method=method, path=path).inc()

        return response


# --- Metrics endpoint handler ----------------------------------------------


def metrics_response() -> Response:
    """Generate Prometheus text exposition format."""
    body = generate_latest(REGISTRY)
    return Response(content=body, media_type="text/plain; charset=utf-8")
