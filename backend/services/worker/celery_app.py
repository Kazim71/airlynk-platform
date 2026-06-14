"""
AirLynk — Celery application factory.

Broker:  RabbitMQ  (ARCHITECTURE.md §4.3, §5)
Backend: Redis     (INFRASTRUCTURE.md §6)

Retry policy follows EVENT_CATALOG.md §Retry Policy:
  - 3 retries maximum
  - Exponential backoff: 5s → 30s → 120s

Run with:
    celery -A backend.services.worker.celery_app worker --loglevel=info
"""

from __future__ import annotations

from celery import Celery

from backend.shared.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "airlynk",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

celery_app.conf.update(
    # Serialisation
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Retry policy (EVENT_CATALOG.md)
    task_default_retry_delay=5,
    task_max_retries=3,
    # Task routing
    task_default_queue="airlynk.default",
    task_create_missing_queues=True,
    # Result backend
    result_expires=3600,  # 1 hour
    # Worker
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    # Acknowledgement
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Auto-discover task modules
celery_app.autodiscover_tasks(["backend.services.worker"])
