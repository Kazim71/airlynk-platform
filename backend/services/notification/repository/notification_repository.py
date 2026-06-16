from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationStatus,
)
from backend.services.notification.schemas.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(self, data: NotificationCreate) -> Notification:
        notification = Notification(**data.model_dump())
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def get_notification(self, notification_id: UUID) -> Notification | None:
        return await self.session.get(Notification, notification_id)

    async def list_notifications_for_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, notification_id: UUID, status: NotificationStatus, error_message: str | None = None) -> None:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status=status, error_message=error_message)
        )
        await self.session.execute(stmt)

    async def mark_as_read(self, notification_id: UUID) -> Notification | None:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(read_at=datetime.now(timezone.utc))
            .returning(Notification)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_template(self, event_type: str) -> NotificationTemplate | None:
        stmt = select(NotificationTemplate).where(
            NotificationTemplate.event_type == event_type,
            NotificationTemplate.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
