"""
AirLynk — Async RabbitMQ connection & publisher.

Topic exchange-based messaging following EVENT_CATALOG.md.  Uses ``aio-pika``
for async AMQP operations.

Exchange strategy:  topic exchanges (EVENT_CATALOG.md §Exchange Strategy)
Naming convention:  service.domain.action
"""

from __future__ import annotations

import json
import logging
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from backend.shared.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

_connection: aio_pika.abc.AbstractRobustConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None
_exchange: aio_pika.abc.AbstractExchange | None = None

EXCHANGE_NAME = "airlynk.events"


async def init_rabbitmq(settings: Settings | None = None) -> None:
    """Open a robust connection, create channel and topic exchange."""
    global _connection, _channel, _exchange
    settings = settings or get_settings()
    _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    _channel = await _connection.channel()
    _exchange = await _channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,
    )
    logger.info("RabbitMQ connection established", extra={"exchange": EXCHANGE_NAME})


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
        msg = "RabbitMQ not initialised. Call init_rabbitmq() during startup."
        raise RuntimeError(msg)

    message = Message(
        body=json.dumps(payload, default=str).encode(),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await _exchange.publish(message, routing_key=routing_key)
    logger.debug("Event published", extra={"routing_key": routing_key})


async def rabbitmq_health_check() -> bool:
    """Return True if the RabbitMQ connection is alive."""
    try:
        return _connection is not None and not _connection.is_closed
    except Exception:
        return False
