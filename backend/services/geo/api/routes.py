"""
AirLynk — Geo API Routes.
"""
from fastapi import APIRouter
from backend.services.geo.schemas.geo import RouteRequest, RouteEstimateResponse
from backend.services.geo.service.geo_service import GeoService

router = APIRouter(prefix="/geo", tags=["Geo Intelligence"])

@router.post("/estimate", response_model=RouteEstimateResponse)
async def estimate_route(req: RouteRequest):
    """Estimate distance and ETA for a given route."""
    service = GeoService()
    return await service.estimate_route(req)
