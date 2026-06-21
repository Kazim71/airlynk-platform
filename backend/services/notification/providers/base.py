from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class BaseNotificationProvider(ABC):
    """Abstract base class for outbound notification providers."""

    @abstractmethod
    async def send(
        self, user_id: UUID, title: str, message: str, data: dict[str, Any] | None = None
    ) -> bool:
        """
        Sends the notification via the provider.
        Returns True if successful. Raises Exception if it should be retried or failed.
        """
        pass
