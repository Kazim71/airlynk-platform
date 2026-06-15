"""
AirLynk — Email Notification Provider.
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


class EmailProvider(NotificationProvider):
    """Mock implementation of an Email provider (e.g. SendGrid, Amazon SES)."""

    async def send(
        self, recipient: str, title: str, content: str, payload: dict[str, Any] | None = None
    ) -> bool:
        start_time = time.perf_counter()
        try:
            # --- MOCK IMPLEMENTATION ---
            logger.info(
                "Simulating email delivery",
                extra={
                    "channel": "EMAIL",
                    "recipient": recipient,
                    "title": title,
                },
            )

            # Simulate network delay
            # await asyncio.sleep(0.1)

            NOTIFICATION_SEND_TOTAL.labels(channel="email").inc()
            return True
        except Exception as e:
            NOTIFICATION_FAILURES_TOTAL.labels(channel="email").inc()
            logger.error(f"Email delivery failed: {e}", exc_info=True)
            raise
        finally:
            duration = time.perf_counter() - start_time
            NOTIFICATION_PROVIDER_LATENCY.labels(channel="email").observe(duration)
