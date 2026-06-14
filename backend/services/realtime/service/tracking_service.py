"""
AirLynk — Realtime Tracking Service.
"""

import json
import logging
from datetime import UTC, datetime
from uuid import UUID

from backend.services.realtime.schemas.tracking import LocationUpdate, RealtimeEvent
from backend.services.realtime.websocket.manager import manager
from backend.shared.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Keys
REDIS_KEY_DRIVER_LOCATIONS = "realtime:driver_locations"
REDIS_KEY_PREFIX_DRIVER_PRESENCE = "realtime:driver:presence:"

# Channels
CHANNEL_DRIVER_PREFIX = "realtime:driver:"
CHANNEL_BOOKING_PREFIX = "realtime:booking:"
CHANNEL_OPERATORS = "realtime:operators"

class TrackingService:
    """Handles driver location updates and presence tracking."""

    @staticmethod
    async def update_driver_location(driver_id: UUID, location: LocationUpdate) -> None:
        """Store the driver's location in Redis and broadcast the update."""
        redis = get_redis_client()

        try:
            # 1. Store in Redis GEO (longitude, latitude, member)
            print(f"[DEBUG] Adding to GEO: {location.lng}, {location.lat}, {driver_id}")
            await redis.geoadd(
                REDIS_KEY_DRIVER_LOCATIONS,
                (location.lng, location.lat, str(driver_id))
            )

            # 2. Update driver presence TTL (expires after 60 seconds)
            presence_key = f"{REDIS_KEY_PREFIX_DRIVER_PRESENCE}{driver_id}"
            await redis.setex(presence_key, 60, "active")

            # 3. Broadcast to driver's personal channel and to operators.
            event = RealtimeEvent(
                event="driver.location_updated",
                data={
                    "driver_id": str(driver_id),
                    "lat": location.lat,
                    "lng": location.lng,
                    "heading": location.heading,
                    "speed": location.speed,
                    "timestamp": location.timestamp.isoformat()
                }
            )
            event_json = event.model_dump_json()

            # Broadcast
            driver_channel = f"{CHANNEL_DRIVER_PREFIX}{driver_id}"
            print(f"[DEBUG] Broadcasting to {driver_channel} and {CHANNEL_OPERATORS}")
            await manager.broadcast_to_channel(driver_channel, event_json)
            await manager.broadcast_to_channel(CHANNEL_OPERATORS, event_json)
            print("[DEBUG] Broadcast complete")
        except Exception as e:
            logger.error(f"Error updating driver location: {e}")
            raise

    @staticmethod
    async def get_active_drivers() -> list[str]:
        """Get a list of currently active driver IDs (those with presence)."""
        redis = get_redis_client()
        
        # In a real system, scanning keys might be slow, so a Sorted Set with timestamps 
        # is often better. For this monolith, SCAN on presence keys is acceptable or
        # relying on the active dispatch pool.
        # Let's use a simple pattern scan for now.
        cursor = 0
        active_drivers = []
        while True:
            cursor, keys = await redis.scan(cursor, match=f"{REDIS_KEY_PREFIX_DRIVER_PRESENCE}*")
            for key in keys:
                driver_id = key.replace(REDIS_KEY_PREFIX_DRIVER_PRESENCE, "")
                active_drivers.append(driver_id)
            if cursor == 0:
                break
        return active_drivers

