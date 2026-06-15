# ADR 004: OpenTelemetry for Distributed Tracing

## Status
Accepted

## Context
With asynchronous workflows moving from FastAPI to RabbitMQ and Celery, diagnosing performance bottlenecks and errors requires a unified view of request lifecycles across boundaries.

## Decision
We will use OpenTelemetry (OTel) to instrument FastAPI, SQLAlchemy, Redis, and Celery. Traces will be propagated using W3C Trace Context headers injected into HTTP requests and RabbitMQ AMQP message headers. Traces will be ingested by Grafana Tempo and correlated with Loki structured JSON logs via the `trace_id`.

## Consequences
- **Pros**: Vendor-agnostic instrumentation, deep visibility into async workflows, correlation between logs and traces.
- **Cons**: Added complexity in configuring exporters and ensuring context propagation in custom asynchronous loops (like WebSockets).
