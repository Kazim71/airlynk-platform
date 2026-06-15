"""
AirLynk — Surge Pricing Celery Tasks.
"""

from __future__ import annotations

import logging

from backend.services.pricing.events.publishers import publish_pricing_surge_changed
from backend.shared.cache.redis_client import get_redis_client
from backend.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="pricing.recompute_surge_regions")  # type: ignore
def recompute_surge_regions() -> None:
    """
    Periodically compute the surge multipliers for active cities.
    In a real system, this would read metrics like active bookings and available drivers.
    For this implementation, we apply a mock algorithm.
    """
    import asyncio

    # We need to run the async redis update inside the sync celery task
    async def _update_surge() -> None:
        redis = get_redis_client()
        # Mock logic: iterate over supported cities and calculate a dynamic surge
        cities = ["New York", "London", "San Francisco"]
        for city in cities:
            key = f"pricing:surge:{city.lower()}"
            # For demonstration, randomly set a surge multiplier between 1.0 and 2.5
            import random

            new_surge = round(random.uniform(1.0, 2.5), 2)
            await redis.setex(key, 300, str(new_surge))  # expire in 5 minutes

            logger.info(f"Updated surge multiplier for {city}: {new_surge}x")
            # Publish event
            await publish_pricing_surge_changed(city, float(new_surge))

    asyncio.run(_update_surge())


@celery_app.task(name="pricing.cleanup_expired_surge")  # type: ignore
def cleanup_expired_surge() -> None:
    """
    Cleanup expired surge regions.
    Redis handles expiration automatically via TTL, but we could add manual cleanup here if needed.
    """
    logger.info("Executed cleanup_expired_surge task")
