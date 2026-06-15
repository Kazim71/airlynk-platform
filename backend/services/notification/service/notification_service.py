"""
AirLynk — Notification Service.

Handles event routing, templating, and dispatching.
"""

import json
import logging
import uuid
from string import Template
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification.models.notification import (
    DeliveryStatus,
    NotificationChannel,
)
from backend.services.notification.providers.email import EmailProvider
from backend.services.notification.providers.push import PushProvider
from backend.services.notification.providers.sms import SMSProvider
from backend.services.notification.repository.notification_repository import NotificationRepository
from backend.services.notification.schemas.notification import NotificationCreate
from backend.shared.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Registry of providers
PROVIDERS = {
    NotificationChannel.EMAIL: EmailProvider(),
    NotificationChannel.SMS: SMSProvider(),
    NotificationChannel.PUSH: PushProvider(),
}


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = NotificationRepository(session)
        self.redis = get_redis_client()

    async def _is_duplicate_event(self, event_id: str | None) -> bool:
        if not event_id:
            return False
        # Use Redis to deduplicate
        key = f"notify:dedup:{event_id}"
        is_new = await self.redis.setnx(key, "1")
        if is_new:
            await self.redis.expire(key, 86400)  # 24 hours
        return not is_new

    def _render_template(self, template_str: str, payload: dict[str, Any]) -> str:
        if not template_str:
            return ""
        try:
            return Template(template_str).safe_substitute(payload)
        except Exception:
            return template_str

    async def process_event(
        self, event_name: str, payload: dict[str, Any], event_id: str | None = None
    ) -> None:
        """Process an incoming domain event and generate notifications."""
        if await self._is_duplicate_event(event_id):
            logger.info("Skipping duplicate event", extra={"event_id": event_id})
            return

        # Try to extract user_id
        user_id_str = (
            payload.get("user_id") or payload.get("customer_id") or payload.get("driver_id")
        )
        if not user_id_str:
            logger.warning(f"No user_id found in event {event_name}")
            return

        user_id = uuid.UUID(user_id_str)

        # We need to dispatch to multiple channels
        # Get preferences
        prefs = await self.repo.get_user_preferences(user_id)

        channels_to_send = []
        if prefs.email_enabled:
            channels_to_send.append(NotificationChannel.EMAIL)
        if prefs.sms_enabled:
            channels_to_send.append(NotificationChannel.SMS)
        if prefs.push_enabled:
            channels_to_send.append(NotificationChannel.PUSH)

        # Always send to WebSocket for active sessions
        channels_to_send.append(NotificationChannel.WEBSOCKET)

        # Base title/content fallback
        base_title = f"New activity: {event_name}"
        base_content = json.dumps(payload)

        # Check for templates. If none, we use fallback.
        # But for an MVP, we will generate the notification record first.
        # We can try to look up an EMAIL template to form the base notification.
        template = await self.repo.get_template(event_name, NotificationChannel.EMAIL)
        if template:
            base_title = self._render_template(template.subject_template or base_title, payload)
            base_content = self._render_template(template.body_template, payload)

        # 1. Create Notification record
        notification = await self.repo.create_notification(
            NotificationCreate(
                user_id=user_id, title=base_title, content=base_content, metadata_payload=payload
            )
        )

        # 2. Create delivery records and dispatch
        from backend.services.notification.worker import deliver_notification

        for channel in channels_to_send:
            delivery = await self.repo.create_delivery(notification.id, channel)

            # Enqueue celery task for async delivery
            deliver_notification.delay(
                delivery_id=str(delivery.id),
                channel=channel.value,
                recipient=str(
                    user_id
                ),  # We use user_id as recipient; in reality we'd lookup email/phone from users table
                title=base_title,
                content=base_content,
                payload=payload,
            )

        await self.session.commit()

    async def process_delivery(
        self,
        delivery_id: uuid.UUID,
        channel_str: str,
        recipient: str,
        title: str,
        content: str,
        payload: dict[str, Any],
    ) -> None:
        """Executed by Celery worker to perform the actual delivery."""
        channel = NotificationChannel(channel_str)

        if channel == NotificationChannel.WEBSOCKET:
            # WebSocket dispatch
            from backend.services.realtime.websocket.manager import manager

            await manager.broadcast_to_channel(
                f"user:{recipient}",
                json.dumps({"type": "NOTIFICATION", "title": title, "content": content}),
            )
            await self.repo.update_delivery_status(
                delivery_id, DeliveryStatus.SENT, increment_attempt=True
            )
            await self.session.commit()
            return

        provider = PROVIDERS.get(channel)
        if not provider:
            logger.error(f"No provider configured for channel {channel}")
            await self.repo.update_delivery_status(
                delivery_id,
                DeliveryStatus.FAILED,
                error_message="No provider",
                increment_attempt=True,
            )
            await self.session.commit()
            return

        try:
            await provider.send(recipient, title, content, payload)
            await self.repo.update_delivery_status(
                delivery_id, DeliveryStatus.SENT, increment_attempt=True
            )
            await self.session.commit()
        except Exception as e:
            await self.repo.update_delivery_status(
                delivery_id, DeliveryStatus.FAILED, error_message=str(e), increment_attempt=True
            )
            await self.session.commit()
            raise  # Re-raise for celery retry
