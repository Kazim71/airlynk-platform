"""
AirLynk — Notification Provider Interfaces.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Abstract base class for all notification delivery providers."""

    @abstractmethod
    async def send(
        self, recipient: str, title: str, content: str, payload: dict[str, Any] | None = None
    ) -> bool:
        """
        Deliver a notification to the specified recipient.

        Args:
            recipient: The delivery target (email, phone number, device token).
            title: The subject or title of the notification.
            content: The main body of the notification.
            payload: Additional metadata payload for the channel.

        Returns:
            True if delivery succeeded (or was enqueued successfully by the provider).

        Raises:
            Exception if delivery fails and should be retried.
        """
        pass
