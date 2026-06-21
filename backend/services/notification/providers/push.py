import asyncio
import logging
from typing import Any
from uuid import UUID

from backend.services.notification.providers.base import BaseNotificationProvider

logger = logging.getLogger(__name__)


class PushProvider(BaseNotificationProvider):
    """Mock Push Notification provider (e.g. FCM/APNS)."""

    async def send(
        self, user_id: UUID, title: str, message: str, data: dict[str, Any] | None = None
    ) -> bool:
        logger.info(f"Delivering PUSH to user {user_id} | Title: {title} | Body: {message}")
        # Simulate network latency
        await asyncio.sleep(0.2)
        return True
