# ADR 007: Distributed Locking Strategy

## Status
Accepted

## Context
During dispatch and booking workflows, concurrent requests or workers might attempt to modify the same booking or assign the same driver simultaneously.

## Decision
We implement distributed locking using Redis (via a custom lock context manager or `redis-py` locks) to ensure mutually exclusive access to critical resources across multiple FastAPI or Celery nodes.

## Consequences
Pros: Prevents race conditions and double-dispatch.
Cons: Requires careful lock timeouts and TTL management to prevent deadlocks if a worker crashes holding the lock.
