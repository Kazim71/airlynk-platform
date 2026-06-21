"""
AirLynk — Geo Service using Haversine calculation.
"""

import math

from backend.services.geo.schemas.geo import RouteEstimateResponse, RouteRequest


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r_earth * c


class GeoService:
    async def estimate_route(self, req: RouteRequest) -> RouteEstimateResponse:
        distance_km = haversine(req.pickup_lat, req.pickup_lng, req.dropoff_lat, req.dropoff_lng)

        # Mock logic: average speed in city traffic ~ 30 km/h, so 2 mins per km.
        # Add a base of 5 mins for picking up.
        duration_minutes = int(distance_km * 2.0) + 5

        # Mock surge logic based on some simple coordinate heuristics
        is_surge = False
        if 28.5 < req.pickup_lat < 28.7 and 77.0 < req.pickup_lng < 77.3:
            # Delhi is always surging in our mock!
            is_surge = True

        return RouteEstimateResponse(
            distance_km=round(distance_km, 2),
            duration_minutes=duration_minutes,
            is_surge_active=is_surge,
        )
