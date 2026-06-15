"""
AirLynk — Notification Repository.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.notification.models.notification import (
    DeliveryStatus,
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationStatus,
    NotificationTemplate,
    UserNotificationPreference,
)
from backend.services.notification.schemas.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_notification(self, data: NotificationCreate) -> Notification:
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            content=data.content,
            metadata_payload=data.metadata_payload,
            status=NotificationStatus.PENDING,
        )
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def create_delivery(
        self, notification_id: uuid.UUID, channel: NotificationChannel
    ) -> NotificationDelivery:
        delivery = NotificationDelivery(
            notification_id=notification_id,
            channel=channel,
            status=DeliveryStatus.PENDING,
            attempt_count=0,
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def get_notification_with_deliveries(
        self, notification_id: uuid.UUID
    ) -> Notification | None:
        stmt = (
            select(Notification)
            .where(Notification.id == notification_id)
            .options(selectinload(Notification.deliveries))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_delivery_status(
        self,
        delivery_id: uuid.UUID,
        status: DeliveryStatus,
        error_message: str | None = None,
        increment_attempt: bool = False,
    ) -> None:
        updates: dict[str, Any] = {"status": status}
        if error_message is not None:
            updates["error_message"] = error_message
        if status == DeliveryStatus.SENT:
            updates["sent_at"] = datetime.now(UTC)

        stmt = (
            update(NotificationDelivery)
            .where(NotificationDelivery.id == delivery_id)
            .values(**updates)
        )
        if increment_attempt:
            stmt = stmt.values(attempt_count=NotificationDelivery.attempt_count + 1)

        await self.session.execute(stmt)
        await self.session.flush()

    async def update_notification_status(
        self, notification_id: uuid.UUID, status: NotificationStatus
    ) -> None:
        stmt = update(Notification).where(Notification.id == notification_id).values(status=status)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_user_preferences(self, user_id: uuid.UUID) -> UserNotificationPreference:
        stmt = select(UserNotificationPreference).where(
            UserNotificationPreference.user_id == user_id
        )
        result = await self.session.execute(stmt)
        pref = result.scalar_one_or_none()
        if not pref:
            pref = UserNotificationPreference(user_id=user_id)
            self.session.add(pref)
            await self.session.flush()
        return pref

    async def get_template(
        self, event_name: str, channel: NotificationChannel
    ) -> NotificationTemplate | None:
        stmt = select(NotificationTemplate).where(
            NotificationTemplate.event_name == event_name,
            NotificationTemplate.channel == channel,
            NotificationTemplate.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .options(selectinload(Notification.deliveries))
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def mark_as_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Notification | None:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(read_at=datetime.now(UTC))
            .returning(Notification)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
