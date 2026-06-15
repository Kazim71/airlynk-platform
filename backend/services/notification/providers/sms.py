"""
AirLynk — SMS Notification Provider.
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


class SMSProvider(NotificationProvider):
    """Mock implementation of an SMS provider (e.g. Twilio, AWS SNS)."""

    async def send(
        self, recipient: str, title: str, content: str, payload: dict[str, Any] | None = None
    ) -> bool:
        start_time = time.perf_counter()
        try:
            # --- MOCK IMPLEMENTATION ---
            logger.info(
                "Simulating SMS delivery",
                extra={
                    "channel": "SMS",
                    "recipient": recipient,
                    "content_length": len(content),
                },
            )

            NOTIFICATION_SEND_TOTAL.labels(channel="sms").inc()
            return True
        except Exception as e:
            NOTIFICATION_FAILURES_TOTAL.labels(channel="sms").inc()
            logger.error(f"SMS delivery failed: {e}", exc_info=True)
            raise
        finally:
            duration = time.perf_counter() - start_time
            NOTIFICATION_PROVIDER_LATENCY.labels(channel="sms").observe(duration)
