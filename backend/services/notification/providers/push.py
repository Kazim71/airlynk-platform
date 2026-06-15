"""
AirLynk — Push Notification Provider.
"""

import logging
import time
from typing import Any

from backend.services.notification.providers.base import NotificationProvider
from backend.shared.observability.metrics import (
    NOTIFICATION_FAILURES_TOTAL,
    NOTIFICATION_PROVIDER_LATENCY,
    NOTIFICATION_SEND_TOTAL,
)

logger = logging.getLogger(__name__)


class PushProvider(NotificationProvider):
    """Mock implementation of a Push provider (e.g. FCM, APNs)."""

    async def send(
        self, recipient: str, title: str, content: str, payload: dict[str, Any] | None = None
    ) -> bool:
        start_time = time.perf_counter()
        try:
            # --- MOCK IMPLEMENTATION ---
            logger.info(
                "Simulating Push delivery",
                extra={
                    "channel": "PUSH",
                    "recipient": recipient,
                    "title": title,
                },
            )

            NOTIFICATION_SEND_TOTAL.labels(channel="push").inc()
            return True
        except Exception as e:
            NOTIFICATION_FAILURES_TOTAL.labels(channel="push").inc()
            logger.error(f"Push delivery failed: {e}", exc_info=True)
            raise
        finally:
            duration = time.perf_counter() - start_time
            NOTIFICATION_PROVIDER_LATENCY.labels(channel="push").observe(duration)
