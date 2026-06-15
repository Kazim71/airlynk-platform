# Metrics Catalog

This document outlines the custom Prometheus metrics exposed by the AirLynk platform.

## Business Metrics
| Metric Name | Type | Description |
|-------------|------|-------------|
| `airlynk_bookings_created_total` | Counter | Total bookings created in the system. |
| `airlynk_bookings_completed_total` | Counter | Total bookings successfully completed. |
| `airlynk_dispatch_attempts_total` | Counter | Total dispatch attempts made to drivers. |
| `airlynk_dispatch_assignment_retries_total` | Counter | Total number of times a dispatch assignment was retried. |
| `airlynk_dispatch_timeouts_total` | Counter | Total driver dispatch timeouts. |
| `airlynk_driver_acceptance_total` | Counter | Total times a driver accepted a dispatch offer. |
| `airlynk_websocket_messages_total` | Counter | Total messages broadcasted over WebSockets. |

## Infrastructure & Domain Metrics
| Metric Name | Type | Description |
|-------------|------|-------------|
| `airlynk_websocket_active_connections` | Gauge | Current active WebSocket connections grouped by domain. |
| `airlynk_rabbitmq_messages_published_total` | Counter | Total messages successfully published to RabbitMQ. |
| `airlynk_rabbitmq_messages_consumed_total` | Counter | Total messages consumed from RabbitMQ queues. |
| `airlynk_rabbitmq_publish_failures_total` | Counter | Total failures when attempting to publish to RabbitMQ. |
| `airlynk_redis_operation_failures_total` | Counter | Total failures when interacting with Redis. |
| `airlynk_celery_task_duration_seconds` | Histogram | Execution duration for Celery tasks. |
