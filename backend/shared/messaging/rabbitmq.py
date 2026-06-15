"""
AirLynk — Async RabbitMQ connection & publisher.

Topic exchange-based messaging following EVENT_CATALOG.md.  Uses ``aio-pika``
for async AMQP operations.

Exchange strategy:  topic exchanges (EVENT_CATALOG.md §Exchange Strategy)
Naming convention:  service.domain.action
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from opentelemetry import propagate, trace

from backend.shared.config.settings import Settings, get_settings
from backend.shared.observability.metrics import (
    RABBITMQ_MESSAGES_CONSUMED,
    RABBITMQ_MESSAGES_PUBLISHED,
    RABBITMQ_PUBLISH_FAILURES,
)

logger = logging.getLogger(__name__)

_connection: aio_pika.abc.AbstractRobustConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None
_exchange: aio_pika.abc.AbstractExchange | None = None
_retry_task: asyncio.Task[None] | None = None

EXCHANGE_NAME = "airlynk.events"


_post_connect_hooks: list[Any] = []


def register_consumer_setup(hook: Any) -> None:
    """Register a hook to run when RabbitMQ connects."""
    _post_connect_hooks.append(hook)


async def _connect_with_retry(settings: Settings) -> None:
    """Background task to connect to RabbitMQ with exponential backoff."""
    global _connection, _channel, _exchange
    attempt = 1
    backoff = 2

    while True:
        try:
            _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            _channel = await _connection.channel()
            _exchange = await _channel.declare_exchange(
                EXCHANGE_NAME,
                ExchangeType.TOPIC,
                durable=True,
            )
            logger.info("RabbitMQ connection established", extra={"exchange": EXCHANGE_NAME})

            # Start consumers
            for hook in _post_connect_hooks:
                try:
                    await hook()
                except Exception as e:
                    logger.error(f"Failed to run post-connect hook: {e}")
            break
        except Exception as e:
            logger.warning(
                "RabbitMQ connection failed, retrying in background",
                extra={
                    "attempt": attempt,
                    "target": settings.rabbitmq_url,
                    "backoff_seconds": backoff,
                    "error": str(e),
                },
            )
            await asyncio.sleep(backoff)
            attempt += 1
            backoff = min(backoff * 2, 30)


async def init_rabbitmq(settings: Settings | None = None) -> None:
    """Start background connection loop without blocking API startup."""
    global _retry_task
    settings = settings or get_settings()
    _retry_task = asyncio.create_task(_connect_with_retry(settings))


async def close_rabbitmq() -> None:
    """Gracefully close channel and connection — called during shutdown."""
    global _connection, _channel, _exchange
    if _channel is not None:
        await _channel.close()
    if _connection is not None:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None
    logger.info("RabbitMQ connection closed")


async def publish_event(routing_key: str, payload: dict[str, Any]) -> None:
    """Publish a JSON message to the topic exchange.

    Args:
        routing_key: Event name following ``service.domain.action`` convention.
        payload: Serialisable dict — typically an ``EventEnvelope.model_dump()``.
    """
    if _exchange is None:
        logger.warning(
            "Event dropped because RabbitMQ is not connected", extra={"routing_key": routing_key}
        )
        return

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        f"publish {routing_key}",
        kind=trace.SpanKind.PRODUCER,
        attributes={"messaging.system": "rabbitmq", "messaging.destination": EXCHANGE_NAME},
    ):
        headers: dict[str, Any] = {}
        propagate.inject(headers)

        message = Message(
            body=json.dumps(payload, default=str).encode(),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
            headers=headers,
        )
        try:
            await _exchange.publish(message, routing_key=routing_key)
            RABBITMQ_MESSAGES_PUBLISHED.labels(routing_key=routing_key).inc()
            logger.debug("Event published", extra={"routing_key": routing_key})
        except Exception as e:
            RABBITMQ_PUBLISH_FAILURES.inc()
            logger.error(f"Failed to publish to RabbitMQ: {e}")
            raise


async def rabbitmq_health_check() -> bool:
    """Return True if the RabbitMQ connection is alive."""
    try:
        return _connection is not None and not _connection.is_closed
    except Exception:
        return False


async def start_consumer(
    queue_name: str,
    routing_keys: list[str],
    callback: Any,
) -> None:
    """Declare a queue, bind it to routing keys on the topic exchange, and start consuming."""
    if _channel is None or _exchange is None:
        logger.error("Cannot start consumer: RabbitMQ is not connected.")
        return

    try:
        queue = await _channel.declare_queue(queue_name, durable=True)
        for rk in routing_keys:
            await queue.bind(_exchange, routing_key=rk)

        tracer = trace.get_tracer(__name__)

        async def _process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            ctx = propagate.extract(message.headers or {})
            with tracer.start_as_current_span(
                f"consume {message.routing_key}",
                context=ctx,
                kind=trace.SpanKind.CONSUMER,
                attributes={
                    "messaging.system": "rabbitmq",
                    "messaging.destination": queue_name,
                    "messaging.operation": "process",
                },
            ):
                async with message.process():
                    try:
                        RABBITMQ_MESSAGES_CONSUMED.labels(queue_name=queue_name).inc()
                        payload = json.loads(message.body.decode())
                        await callback(payload)
                    except Exception as e:
                        logger.error(f"Error processing RabbitMQ message: {e}")

        await queue.consume(_process_message)
        logger.info(f"Started consuming queue {queue_name} with keys {routing_keys}")
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ consumer {queue_name}: {e}")
