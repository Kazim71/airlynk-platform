# Observability Architecture

## Overview
AirLynk implements a comprehensive observability stack based on OpenTelemetry, Prometheus, Grafana, Tempo, and Loki. This stack provides deep insights into the modular monolith's distributed traces, metrics, and structured logs.

## Components
1. **OpenTelemetry (OTEL)**
   - Used for distributed tracing across FastAPI, SQLAlchemy, Redis, and Celery.
   - Traces are exported via OTLP to Tempo.

2. **Prometheus**
   - Scrapes metrics from `/metrics` endpoint.
   - Stores custom business metrics and infrastructure metrics.
   - Evaluates alerting rules.

3. **Grafana**
   - The primary visualization interface.
   - Provisions data sources and dashboards automatically.

4. **Tempo**
   - Distributed tracing backend.
   - Correlates trace IDs with logs via Loki.

5. **Loki & Promtail**
   - Log aggregation. Promtail scrapes Docker logs and forwards them to Loki.

## Context Propagation
- OTEL context is propagated via AMQP headers in RabbitMQ.
- Celery injects trace context across worker boundaries.
- WebSocket payloads inject span contexts where necessary.
