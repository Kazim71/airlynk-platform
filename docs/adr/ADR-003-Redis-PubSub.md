# ADR 003: Redis Pub/Sub for Realtime WebSockets

## Status
Accepted

## Context
WebSockets require stateful connections. If the API scales horizontally, a broadcast event might be triggered on an API node that does not hold the target client's WebSocket connection.

## Decision
We use Redis Pub/Sub as the bridging mechanism. Each API node subscribes to Redis channels for its connected WebSockets. When a message is broadcast, it goes to Redis and is pushed to all nodes.

## Consequences
Pros: Easy horizontal scaling of WebSocket connections.
Cons: Redis Pub/Sub is fire-and-forget; disconnected clients will miss messages.
