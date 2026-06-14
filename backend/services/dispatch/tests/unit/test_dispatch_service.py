"""
AirLynk — Dispatch Unit Tests.
"""

from uuid import uuid4

from backend.services.booking.models.booking import Booking
from backend.services.dispatch.service.matching_engine import MatchingEngine


def test_matching_engine_sorting() -> None:
    engine = MatchingEngine()
    booking = Booking(id=uuid4())

    drivers = [
        {"driver_id": str(uuid4()), "latitude": 0.1, "longitude": 0.1},
        {"driver_id": str(uuid4()), "latitude": 0.05, "longitude": 0.05},
        {"driver_id": str(uuid4()), "latitude": 0.5, "longitude": 0.5},
    ]

    # Pickup at 0,0
    scored = engine.score_drivers(booking, drivers, 0.0, 0.0)

    assert len(scored) == 3
    # The closest one (0.05, 0.05) should have the highest score
    assert scored[0].driver_id == drivers[1]["driver_id"]
    assert scored[1].driver_id == drivers[0]["driver_id"]
    assert scored[2].driver_id == drivers[2]["driver_id"]
    
    assert scored[0].score > scored[1].score
    assert scored[1].score > scored[2].score


def test_matching_engine_distance() -> None:
    distance = MatchingEngine.calculate_distance(0.0, 0.0, 1.0, 1.0)
    # Roughly ~157km
    assert 150 < distance < 160
