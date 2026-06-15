"""
AirLynk — WebSocket Connection Manager.

Manages active websocket connections and listens to Redis Pub/Sub
to broadcast events to connected clients, enabling horizontal scalability.
"""

import asyncio
import logging
from typing import Any

from fastapi import WebSocket
from redis.asyncio.client import PubSub

from backend.shared.cache.redis_client import get_redis_client
from backend.shared.observability.metrics import (
    WEBSOCKET_ACTIVE_CONNECTIONS,
    WEBSOCKET_MESSAGES_TOTAL,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSockets and Redis Pub/Sub subscriptions."""

    def __init__(self) -> None:
        # dict mapping channel name to list of connected websockets
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.pubsub_task: asyncio.Task[Any] | None = None
        self._pubsub: PubSub | None = None

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept a websocket and add it to the specified channel."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")
        domain = channel.split(":")[0] if ":" in channel else channel
        WEBSOCKET_ACTIVE_CONNECTIONS.labels(domain=domain).inc()

        if not self.pubsub_task:
            await self.start_redis_listener()

        # Subscribe to the Redis channel if it's the first connection for this channel
        if self._pubsub and len(self.active_connections[channel]) == 1:
            await self._pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")

    async def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Remove a websocket from the channel."""
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
                logger.info(f"WebSocket disconnected from channel: {channel}")
                domain = channel.split(":")[0] if ":" in channel else channel
                WEBSOCKET_ACTIVE_CONNECTIONS.labels(domain=domain).dec()

                # Unsubscribe from Redis if no more clients
                if not self.active_connections[channel]:
                    del self.active_connections[channel]
                    if self._pubsub:
                        await self._pubsub.unsubscribe(channel)
                        logger.info(f"Unsubscribed from Redis channel: {channel}")
            except ValueError:
                pass

    async def start_redis_listener(self) -> None:
        """Start a background task to listen to Redis PubSub."""
        redis = get_redis_client()
        self._pubsub = redis.pubsub()
        self.pubsub_task = asyncio.create_task(self._listen_to_redis())
        logger.info("Started Redis Pub/Sub listener for WebSockets")

    async def _listen_to_redis(self) -> None:
        """Listen for messages on Redis and broadcast to WebSockets."""
        if not self._pubsub:
            return

        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]

                    # Ensure string
                    if isinstance(channel, bytes):
                        channel = channel.decode("utf-8")
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")


                    if channel in self.active_connections:
                        # Send to all websockets in this channel
                        disconnected = []
                        for ws in self.active_connections[channel]:
                            try:
                                await ws.send_text(data)
                            except Exception:
                                disconnected.append(ws)

                        # Cleanup dead connections
                        for ws in disconnected:
                            await self.disconnect(ws, channel)
        except Exception:
            pass
        finally:
            self.pubsub_task = None
            self._pubsub = None

    async def broadcast_to_channel(self, channel: str, message: str) -> None:
        """Publish a message to a Redis channel (which will reach all instances)."""
        redis = get_redis_client()
        await redis.publish(channel, message)
        WEBSOCKET_MESSAGES_TOTAL.inc()


# Singleton instance
manager = ConnectionManager()
