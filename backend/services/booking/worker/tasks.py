"""
AirLynk — Booking Background Tasks.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="booking.audit_transition")  # type: ignore
def audit_booking_transition(booking_id: str, old_status: str, new_status: str) -> dict[str, Any]:
    """Async background task to persist audit events to a data lake or external system."""
    logger.info(f"Auditing transition for booking {booking_id}: {old_status} -> {new_status}")
    # In a real system, this might send to S3, BigQuery, etc.
    return {"status": "success", "booking_id": booking_id}


@celery_app.task(name="booking.timeout_cleanup")  # type: ignore
def booking_timeout_cleanup() -> dict[str, Any]:
    """Periodic task to sweep for bookings that have timed out waiting for assignment."""
    logger.info("Running booking timeout cleanup sweep")
    # This would execute a DB query to find CREATED bookings > 30 mins old
    # and transition them to FAILED or CANCELLED, publishing an event.
    return {"status": "success", "processed": 0}
