import asyncio
import logging
from typing import Any
from uuid import UUID

from backend.services.notification.providers.base import BaseNotificationProvider

logger = logging.getLogger(__name__)


class EmailProvider(BaseNotificationProvider):
    """Mock Email provider."""

    async def send(
        self, user_id: UUID, title: str, message: str, data: dict[str, Any] | None = None
    ) -> bool:
        logger.info(f"Delivering EMAIL to user {user_id} | Subject: {title} | Body: {message}")
        # Simulate network latency
        await asyncio.sleep(0.5)
        return True
