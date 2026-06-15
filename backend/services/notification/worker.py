"""
AirLynk — Notification Celery Worker.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from backend.shared.database.session import _session_factory as AsyncSessionLocal, init_db
from backend.shared.cache.redis_client import init_redis
from backend.services.notification.service.notification_service import NotificationService
from backend.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

_RETRY_DELAYS = [5, 30, 120]


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True,
    name="airlynk.notification.process_event",
    max_retries=3,
    acks_late=True,
)
def process_notification_event(
    self: Any, event_name: str, payload: dict[str, Any], event_id: str | None = None
) -> dict[str, str]:
    """Process a domain event to generate notifications."""
    logger.info(
        "Processing notification event", extra={"event_name": event_name, "event_id": event_id}
    )

    async def _process() -> None:
        if AsyncSessionLocal is None:
            await init_db()
            await init_redis()
        async with AsyncSessionLocal() as session:  # type: ignore
            service = NotificationService(session)
            await service.process_event(event_name, payload, event_id)

    try:
        asyncio.run(_process())
        return {"status": "processed", "event_name": event_name}
    except Exception as exc:
        retry_num = self.request.retries
        delay = _RETRY_DELAYS[min(retry_num, len(_RETRY_DELAYS) - 1)]
        logger.warning(
            "Notification event processing failed, retrying",
            extra={"event_name": event_name, "retry": retry_num + 1},
        )
        raise self.retry(exc=exc, countdown=delay) from exc


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True,
    name="airlynk.notification.deliver",
    max_retries=3,
    acks_late=True,
)
def deliver_notification(
    self: Any,
    delivery_id: str,
    channel: str,
    recipient: str,
    title: str,
    content: str,
    payload: dict[str, Any],
) -> dict[str, str]:
    """Deliver a notification to a specific channel via its provider."""
    logger.info(
        "Delivering notification",
        extra={"delivery_id": delivery_id, "channel": channel, "recipient": recipient},
    )

    async def _deliver() -> None:
        if AsyncSessionLocal is None:
            await init_db()
            await init_redis()
        async with AsyncSessionLocal() as session:  # type: ignore
            service = NotificationService(session)
            await service.process_delivery(
                uuid.UUID(delivery_id), channel, recipient, title, content, payload
            )

    try:
        asyncio.run(_deliver())
        return {"status": "delivered", "delivery_id": delivery_id, "channel": channel}
    except Exception as exc:
        retry_num = self.request.retries
        delay = _RETRY_DELAYS[min(retry_num, len(_RETRY_DELAYS) - 1)]
        logger.warning(
            "Notification delivery failed, scheduling retry",
            extra={"delivery_id": delivery_id, "retry": retry_num + 1, "channel": channel},
        )
        raise self.retry(exc=exc, countdown=delay) from exc
