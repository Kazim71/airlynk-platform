import json
import logging
from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from backend.services.notification.providers.email import EmailProvider
from backend.services.notification.providers.push import PushProvider
from backend.services.notification.providers.sms import SMSProvider
from backend.services.notification.repository.notification_repository import NotificationRepository
from backend.services.notification.schemas.notification import NotificationCreate
from backend.shared.cache.redis_client import get_redis_client
from backend.shared.database.session import get_db_session

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository
        self.providers = {
            NotificationChannel.EMAIL: EmailProvider(),
            NotificationChannel.SMS: SMSProvider(),
            NotificationChannel.PUSH: PushProvider(),
        }

    async def get_user_notifications(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Notification]:
        return await self.repository.list_notifications_for_user(user_id, limit, offset)

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        notification = await self.repository.get_notification(notification_id)
        if not notification or notification.user_id != user_id:
            return None
        return await self.repository.mark_as_read(notification_id, user_id)

    async def generate_notifications(
        self,
        user_id: UUID,
        event_type: str,
        context: dict[str, Any],
        event_id: str,
        n_type: NotificationType = NotificationType.SYSTEM,
    ) -> list[Notification]:
        """
        Deduplicates, fans out, and generates notifications based on event type.
        This runs inside Celery worker `process_notification_event`.
        """
        from backend.shared.cache.redis_client import get_redis_client

        redis = get_redis_client()
        lock_key = f"notification:dedup:{event_id}"

        # Deduplication check
        if not await redis.setnx(lock_key, "1"):
            logger.info(f"Duplicate event {event_id} skipped.")
            return []
        await redis.expire(lock_key, 3600)  # Lock for 1 hour

        # Load templates (Fallback if missing)
        template = await self.repository.get_template(event_type)
        if template:
            channels = [NotificationChannel(c) for c in template.channels]
            title = template.title_template.format(**context)
            message = template.message_template.format(**context)
        else:
            # Default fallback for missing templates
            channels = [NotificationChannel.IN_APP]
            title = context.get("title", f"Event: {event_type}")
            message = context.get("message", f"A new {event_type} occurred.")

        created_notifications = []
        for channel in channels:
            data = NotificationCreate(
                user_id=user_id,
                type=n_type,
                channel=channel,
                title=title,
                message=message,
                data=context,
                event_id=event_id,
            )
            # Create in database as PENDING
            notif = await self.repository.create_notification(data)
            created_notifications.append(notif)

        return created_notifications

    async def deliver_notification(self, notification_id: UUID) -> None:
        """
        Actually delivers the notification.
        This runs inside Celery worker `deliver_notification`.
        """
        notification = await self.repository.get_notification(notification_id)
        if not notification or notification.status == NotificationStatus.DELIVERED:
            return

        await self.repository.update_status(notification_id, NotificationStatus.PROCESSING)

        try:
            if notification.channel == NotificationChannel.IN_APP:
                # Deliver via WebSockets (Redis Pub/Sub)
                payload = {
                    "type": "notification",
                    "data": {
                        "id": str(notification.id),
                        "title": notification.title,
                        "message": notification.message,
                        "n_type": notification.type.value,
                        "created_at": notification.created_at.isoformat(),
                    },
                }
                redis = get_redis_client()
                await redis.publish(f"user_{notification.user_id}", json.dumps(payload))
            else:
                # Deliver via Mock Providers
                provider = self.providers.get(notification.channel)
                if provider:
                    await provider.send(
                        user_id=notification.user_id,
                        title=notification.title,
                        message=notification.message,
                        data=notification.data,
                    )
                else:
                    raise Exception(f"No provider found for channel {notification.channel}")

            # Mark delivered
            await self.repository.update_status(notification_id, NotificationStatus.DELIVERED)
            logger.info(f"Notification {notification_id} DELIVERED.")

        except Exception as e:
            await self.repository.update_status(notification_id, NotificationStatus.FAILED, str(e))
            logger.error(f"Notification {notification_id} FAILED: {e!s}")
            raise e


async def get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(NotificationRepository(session))
