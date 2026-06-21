from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.services.notification.models.notification import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)


class NotificationBase(BaseModel):
    user_id: UUID
    type: NotificationType
    channel: NotificationChannel
    title: str
    message: str
    data: dict[str, Any] | None = None
    event_id: str | None = None


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: UUID
    status: NotificationStatus
    error_message: str | None = None
    read_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationTemplateBase(BaseModel):
    event_type: str
    channels: list[NotificationChannel]
    title_template: str
    message_template: str
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateResponse(NotificationTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
