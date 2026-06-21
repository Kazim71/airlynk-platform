import asyncio
import logging
from typing import Any
from uuid import UUID

from backend.services.notification.providers.base import BaseNotificationProvider

logger = logging.getLogger(__name__)


class SMSProvider(BaseNotificationProvider):
    """Mock SMS provider (e.g. Twilio)."""

    async def send(
        self, user_id: UUID, title: str, message: str, data: dict[str, Any] | None = None
    ) -> bool:
        logger.info(f"Delivering SMS to user {user_id} | Text: {message}")
        # Simulate network latency
        await asyncio.sleep(0.3)
        return True
