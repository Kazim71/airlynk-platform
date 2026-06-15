"""
AirLynk — Matching Engine.
"""

import math
from dataclasses import dataclass
from uuid import UUID

from backend.services.booking.models.booking import Booking


@dataclass
class DriverScore:
    driver_id: UUID
    score: float
    distance_km: float


class MatchingEngine:
    """Calculates compatibility and scores drivers for a dispatch request."""

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance in kilometers between two points."""
        # Note: This is a simplified Haversine for the matching engine
        # In a real app, this would use PostGIS or a routing engine.
        r = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @staticmethod
    def score_drivers(
        booking: Booking, drivers: list[dict], pickup_lat: float, pickup_lon: float  # type: ignore
    ) -> list[DriverScore]:
        """
        Score a list of drivers based on distance to the pickup location.
        Returns a list of drivers sorted by score (highest is best).

        `drivers` is a list of dictionaries with driver info from Redis.
        """
        scored_drivers = []
        for d in drivers:
            # Parse driver coordinates (default to 0 if missing for safety)
            d_lat = d.get("latitude", 0.0)
            d_lon = d.get("longitude", 0.0)
            driver_id = UUID(d["driver_id"])

            distance_km = MatchingEngine.calculate_distance(pickup_lat, pickup_lon, d_lat, d_lon)

            # Score logic: Closer is better. Base score 100, minus 5 points per km.
            score = max(0.0, 100.0 - (distance_km * 5.0))

            scored_drivers.append(
                DriverScore(driver_id=driver_id, score=score, distance_km=distance_km)
            )

        # Sort descending by score
        scored_drivers.sort(key=lambda x: x.score, reverse=True)
        return scored_drivers
