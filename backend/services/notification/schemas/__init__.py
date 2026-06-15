"""
AirLynk — Notification Schemas Package.
"""

from backend.services.notification.schemas.notification import (
    NotificationCreate,
    NotificationDeliveryResponse,
    NotificationResponse,
    NotificationTemplateResponse,
    UserNotificationPreferenceResponse,
    UserNotificationPreferenceUpdate,
)

__all__ = [
    "NotificationCreate",
    "NotificationDeliveryResponse",
    "NotificationResponse",
    "NotificationTemplateResponse",
    "UserNotificationPreferenceResponse",
    "UserNotificationPreferenceUpdate",
]
