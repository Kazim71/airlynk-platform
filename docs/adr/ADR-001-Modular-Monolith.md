# ADR 001: Modular Monolith Architecture

## Status
Accepted

## Context
AirLynk needs to scale rapidly while maintaining low operational overhead. Microservices introduce network boundaries, distributed data management, and complex deployments.

## Decision
We will use a Modular Monolith architecture. All domains (Auth, Booking, Dispatch, Realtime) will reside in a single repository and run as a single deployable unit (FastAPI app). Domains will communicate via strictly typed interfaces and async events (RabbitMQ) but share the same database instance and Redis cache.

## Consequences
- **Pros**: Simplified deployment, easier refactoring, no network latency between domains, straightforward local development.
- **Cons**: Strict discipline is required to prevent domains from tightly coupling. We must enforce boundary checks through PR reviews and linting.
