# ADR 005: Celery for Background Workers

## Status
Accepted

## Context
RabbitMQ consumers built with `aio_pika` are great for rapid, async event bridging (like WebSockets). However, long-running workflows with complex retries, rate limiting, and state transitions (like Dispatch Assignment) need more robust task management.

## Decision
We use Celery with RabbitMQ as the broker and Redis as the result backend for robust background task processing.

## Consequences
Pros: Built-in retry mechanisms, robust task acknowledgement, extensive tooling.
Cons: Celery is synchronous/multiprocess by default, which creates a paradigm mix with FastAPI's async nature.
