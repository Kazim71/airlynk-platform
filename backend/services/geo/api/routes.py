"""
AirLynk — Geo API Routes.
"""

from typing import Any

from fastapi import APIRouter, Depends

from backend.services.geo.schemas.geo import RouteEstimateResponse, RouteRequest
from backend.services.geo.service.geo_service import GeoService
from backend.shared.middleware.rbac import get_current_user

router = APIRouter(prefix="/geo", tags=["Geo Intelligence"])


@router.post("/estimate", response_model=RouteEstimateResponse)
async def estimate_route(
    req: RouteRequest, user: dict[str, Any] = Depends(get_current_user)
) -> Any:
    """Estimate distance and ETA for a given route."""
    service = GeoService()
    return await service.estimate_route(req)
