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

# --- Business Metrics --------------------------------------------------------

BOOKINGS_CREATED_TOTAL = Counter(
    "airlynk_bookings_created_total",
    "Total bookings created",
    registry=REGISTRY,
)

BOOKINGS_COMPLETED_TOTAL = Counter(
    "airlynk_bookings_completed_total",
    "Total bookings completed",
    registry=REGISTRY,
)

DISPATCH_ATTEMPTS_TOTAL = Counter(
    "airlynk_dispatch_attempts_total",
    "Total dispatch attempts",
    registry=REGISTRY,
)

DISPATCH_ASSIGNMENT_RETRIES = Counter(
    "airlynk_dispatch_assignment_retries_total",
    "Total dispatch assignment retries",
    registry=REGISTRY,
)

DISPATCH_TIMEOUTS_TOTAL = Counter(
    "airlynk_dispatch_timeouts_total",
    "Total dispatch timeouts",
    registry=REGISTRY,
)

DRIVER_ACCEPTANCE_TOTAL = Counter(
    "airlynk_driver_acceptance_total",
    "Total driver acceptances",
    registry=REGISTRY,
)

WEBSOCKET_MESSAGES_TOTAL = Counter(
    "airlynk_websocket_messages_total",
    "Total websocket messages broadcasted",
    registry=REGISTRY,
)

NOTIFICATION_SEND_TOTAL = Counter(
    "airlynk_notification_send_total",
    "Total notifications sent",
    ["channel"],
    registry=REGISTRY,
)

NOTIFICATION_FAILURES_TOTAL = Counter(
    "airlynk_notification_failures_total",
    "Total notification delivery failures",
    ["channel"],
    registry=REGISTRY,
)

NOTIFICATION_RETRY_TOTAL = Counter(
    "airlynk_notification_retry_total",
    "Total notification delivery retries",
    ["channel"],
    registry=REGISTRY,
)

NOTIFICATION_PROVIDER_LATENCY = Histogram(
    "airlynk_notification_provider_latency_seconds",
    "Notification provider delivery latency in seconds",
    ["channel"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

WEBSOCKET_NOTIFICATION_BROADCASTS = Counter(
    "airlynk_websocket_notification_broadcasts_total",
    "Total websocket notifications broadcasted",
    registry=REGISTRY,
)

# --- Domain & Infrastructure Metrics -----------------------------------------

WEBSOCKET_ACTIVE_CONNECTIONS = Gauge(
    "airlynk_websocket_active_connections",
    "Number of active WebSocket connections",
    ["domain"],
    registry=REGISTRY,
)

RABBITMQ_MESSAGES_PUBLISHED = Counter(
    "airlynk_rabbitmq_messages_published_total",
    "Total RabbitMQ messages published",
    ["routing_key"],
    registry=REGISTRY,
)

RABBITMQ_MESSAGES_CONSUMED = Counter(
    "airlynk_rabbitmq_messages_consumed_total",
    "Total RabbitMQ messages consumed",
    ["queue_name"],
    registry=REGISTRY,
)

RABBITMQ_PUBLISH_FAILURES = Counter(
    "airlynk_rabbitmq_publish_failures_total",
    "Total RabbitMQ message publish failures",
    registry=REGISTRY,
)

REDIS_OPERATION_FAILURES = Counter(
    "airlynk_redis_operation_failures_total",
    "Total Redis operation failures",
    registry=REGISTRY,
)

CELERY_TASK_DURATION = Histogram(
    "airlynk_celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
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
