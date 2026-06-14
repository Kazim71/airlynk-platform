"""
AirLynk — Celery task definitions.

These are the foundational async tasks.  Business-logic tasks will be added
as services are implemented.

Retry backoff follows EVENT_CATALOG.md §Retry Delays:
  - 1st retry:  5 seconds
  - 2nd retry: 30 seconds
  - 3rd retry: 120 seconds (2 minutes)
"""

from __future__ import annotations

import logging
from typing import Any

from backend.services.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# Custom retry backoff schedule
_RETRY_DELAYS = [5, 30, 120]


@celery_app.task(
    bind=True,
    name="airlynk.process_event",
    max_retries=3,
    acks_late=True,
)
def process_event(self: Any, event_payload: dict[str, Any]) -> dict[str, str]:
    """Process a domain event from RabbitMQ.

    This is a generic handler — specific event routing will be added as
    services are implemented.
    """
    event_name = event_payload.get("event_name", "unknown")
    correlation_id = event_payload.get("correlation_id", "")

    logger.info(
        "Processing event",
        extra={
            "event_name": event_name,
            "correlation_id": correlation_id,
        },
    )

    try:
        # --- Event processing logic will be added per service ---
        logger.info("Event processed successfully", extra={"event_name": event_name})
        return {"status": "processed", "event_name": event_name}
    except Exception as exc:
        retry_num = self.request.retries
        delay = _RETRY_DELAYS[min(retry_num, len(_RETRY_DELAYS) - 1)]
        logger.warning(
            "Event processing failed, scheduling retry",
            extra={
                "event_name": event_name,
                "retry": retry_num + 1,
                "delay_seconds": delay,
            },
        )
        raise self.retry(exc=exc, countdown=delay) from exc


@celery_app.task(
    bind=True,
    name="airlynk.send_notification_email",
    max_retries=3,
    acks_late=True,
)
def send_notification_email(
    self: Any,
    recipient: str,
    subject: str,
    body: str,
) -> dict[str, str]:
    """Send a notification email asynchronously.

    Actual SMTP integration will be implemented with the Notification Service.
    This task demonstrates the async email delivery pattern from WORKFLOWS.md §6.
    """
    logger.info(
        "Sending notification email",
        extra={"recipient": recipient, "subject": subject},
    )

    try:
        # --- SMTP integration placeholder ---
        logger.info("Email sent successfully", extra={"recipient": recipient})
        return {"status": "sent", "recipient": recipient}
    except Exception as exc:
        retry_num = self.request.retries
        delay = _RETRY_DELAYS[min(retry_num, len(_RETRY_DELAYS) - 1)]
        logger.warning(
            "Email send failed, scheduling retry",
            extra={"recipient": recipient, "retry": retry_num + 1},
        )
        raise self.retry(exc=exc, countdown=delay) from exc
