import asyncio
import logging
from typing import Any
from uuid import UUID

from backend.services.notification.models.notification import NotificationType
from backend.services.notification.repository.notification_repository import NotificationRepository
from backend.services.notification.service.notification_service import NotificationService
from backend.shared.database.session import get_db_session
from backend.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _process_event(
    user_id: UUID,
    event_type: str,
    context: dict[str, Any],
    event_id: str,
    n_type: NotificationType,
) -> list[str]:
    async for session in get_db_session():
        repo = NotificationRepository(session)
        service = NotificationService(repo)
        created = await service.generate_notifications(
            user_id=user_id,
            event_type=event_type,
            context=context,
            event_id=event_id,
            n_type=n_type,
        )
        return [str(n.id) for n in created]
    return []


@celery_app.task(name="notification.process_event", bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def process_notification_event(
    self: Any, user_id: str, event_type: str, context: dict[str, Any], event_id: str, n_type: str
) -> None:
    """Generates notifications and fans out to delivery tasks."""
    logger.info(f"Processing notification event {event_id} for user {user_id}")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        created_ids = loop.run_until_complete(
            _process_event(UUID(user_id), event_type, context, event_id, NotificationType(n_type))
        )
        # Spawn parallel delivery tasks for each generated notification
        for n_id in created_ids:
            deliver_notification.delay(n_id)

    except Exception as exc:
        logger.error(f"Failed to process notification event: {exc}")
        raise self.retry(exc=exc, countdown=2**self.request.retries)


async def _deliver(notification_id: UUID) -> None:
    async for session in get_db_session():
        repo = NotificationRepository(session)
        service = NotificationService(repo)
        await service.deliver_notification(notification_id)


@celery_app.task(name="notification.deliver", bind=True, max_retries=3, acks_late=True)  # type: ignore[untyped-decorator]
def deliver_notification(self: Any, notification_id: str) -> None:
    """Delivers a specific notification via its configured channel."""
    logger.info(f"Delivering notification {notification_id}")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_deliver(UUID(notification_id)))
    except Exception as exc:
        logger.error(f"Failed to deliver notification {notification_id}: {exc}")
        raise self.retry(exc=exc, countdown=5 * (2**self.request.retries))
