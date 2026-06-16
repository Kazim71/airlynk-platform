"""
AirLynk — Notification Models Package.
"""

from backend.services.notification.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)

__all__ = [
    "Notification",
    "NotificationChannel",
    "NotificationStatus",
    "NotificationTemplate",
    "NotificationType",
]
