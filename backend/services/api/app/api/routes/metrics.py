"""
AirLynk — Prometheus metrics endpoint.

``GET /metrics``  — internal-only Prometheus text exposition endpoint.

See API_SPEC.md §5 (Internal Only authentication).
"""

from __future__ import annotations

from fastapi import APIRouter
from starlette.responses import Response

from backend.shared.observability.metrics import metrics_response

router = APIRouter(tags=["Observability"])


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Exposes application metrics in Prometheus text format. Internal only.",
    include_in_schema=False,  # Hidden from public OpenAPI docs
)
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint."""
    return metrics_response()
