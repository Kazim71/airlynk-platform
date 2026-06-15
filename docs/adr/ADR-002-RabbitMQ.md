# ADR 002: RabbitMQ for Asynchronous Messaging

## Status
Accepted

## Context
The Modular Monolith needs to decouple domains. Direct function calls between domains cause tight coupling.

## Decision
We use RabbitMQ with a Topic Exchange (`airlynk.events`) for async domain events (e.g. `booking.created`).

## Consequences
Pros: High reliability, loose coupling.
Cons: Added infrastructure dependency.
