"""
AirLynk — Celery application factory.

Broker:  RabbitMQ  (ARCHITECTURE.md §4.3, §5)
Backend: Redis     (INFRASTRUCTURE.md §6)

Retry policy follows EVENT_CATALOG.md §Retry Policy:
  - 3 retries maximum
  - Exponential backoff: 5s → 30s → 120s

Run with:
    celery -A backend.worker.celery_app worker --loglevel=info
"""

from __future__ import annotations

from typing import Any

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
celery_app.autodiscover_tasks(
    [
        "backend.services.booking.worker",
        "backend.services.dispatch.worker",
        "backend.services.notification.worker",
        "backend.services.pricing.worker",
    ]
)

celery_app.conf.beat_schedule = {
    "recompute_surge_regions_every_minute": {
        "task": "pricing.recompute_surge_regions",
        "schedule": 60.0,
    },
    "cleanup_expired_surge_every_hour": {
        "task": "pricing.cleanup_expired_surge",
        "schedule": 3600.0,
    },
}

import time

from celery.signals import task_postrun, task_prerun, worker_process_init

from backend.shared.observability.metrics import CELERY_TASK_DURATION
from backend.shared.observability.tracing import setup_tracing


@worker_process_init.connect  # type: ignore
def configure_worker_tracing(**kwargs: Any) -> None:
    """Initialise OpenTelemetry inside each Celery worker process."""
    setup_tracing()


_task_start_times: dict[str, float] = {}


@task_prerun.connect  # type: ignore
def task_prerun_handler(task_id: str, task: Any, *args: Any, **kwargs: Any) -> None:
    _task_start_times[task_id] = time.perf_counter()


@task_postrun.connect  # type: ignore
def task_postrun_handler(task_id: str, task: Any, *args: Any, **kwargs: Any) -> None:
    start_time = _task_start_times.pop(task_id, None)
    if start_time is not None:
        duration = time.perf_counter() - start_time
        CELERY_TASK_DURATION.labels(task_name=task.name).observe(duration)
