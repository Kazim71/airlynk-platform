# EVENT_CATALOG.md

# AirLynk Event Catalog

# Messaging Architecture

## Message Broker

RabbitMQ

## Communication Style

Asynchronous event-driven communication.

## Exchange Strategy

Topic exchanges.

## Retry Strategy

Exponential backoff retries using Celery.

## Dead Letter Queue

All failed events routed to DLQ after retry exhaustion.

---

# Event Naming Convention

Format:

service.domain.action

Examples:

* auth.user.login_success
* booking.trip.created
* notification.email.sent

---

# Event Envelope Structure

```json
{
  "event_id": "uuid",
  "event_name": "auth.user.login_success",
  "event_version": "1.0",
  "timestamp": "2026-06-14T10:00:00Z",
  "producer": "auth-service",
  "correlation_id": "uuid",
  "payload": {}
}
```

---

# 1. Authentication Events

## auth.user.registered

### Producer

Auth Service

### Consumers

* Audit Service
* Notification Service

### Purpose

Triggered after successful account registration.

### Payload

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "registered_at": "timestamp"
}
```

---

## auth.user.login_success

### Producer

Auth Service

### Consumers

* Audit Service
* Metrics Service

### Purpose

Triggered after successful login.

### Payload

```json
{
  "user_id": "uuid",
  "ip_address": "127.0.0.1",
  "device_fingerprint": "hash",
  "login_at": "timestamp"
}
```

---

## auth.user.login_failed

### Producer

Auth Service

### Consumers

* Audit Service
* Threat Detection Service

### Purpose

Triggered after failed authentication attempt.

### Payload

```json
{
  "email": "user@example.com",
  "ip_address": "127.0.0.1",
  "attempted_at": "timestamp"
}
```

---

## auth.token.refreshed

### Producer

Auth Service

### Consumers

* Audit Service

### Purpose

Triggered after refresh token rotation.

---

# 2. Booking Events

## booking.trip.created

### Producer

Booking Service

### Consumers

* Notification Service
* Audit Service
* Dispatch Service

### Purpose

Triggered after booking creation.

### Payload

```json
{
  "booking_id": "uuid",
  "customer_id": "uuid",
  "pickup_location": "Airport",
  "dropoff_location": "Hotel"
}
```

---

## booking.trip.assigned

### Producer

Dispatch Service

### Consumers

* Notification Service
* Audit Service

### Purpose

Triggered after driver assignment.

---

## booking.trip.completed

### Producer

Booking Service

### Consumers

* Analytics Service
* Audit Service

### Purpose

Triggered after trip completion.

---

# 3. Notification Events

## notification.email.sent

### Producer

Notification Service

### Consumers

* Audit Service

### Purpose

Track successful email delivery.

---

## notification.email.failed

### Producer

Notification Service

### Consumers

* Monitoring Service

### Purpose

Track failed email delivery attempts.

---

# 4. Security Events

## security.suspicious_activity.detected

### Producer

Threat Detection Service

### Consumers

* Audit Service
* Monitoring Service

### Purpose

Triggered when suspicious behavior exceeds threshold.

### Payload

```json
{
  "user_id": "uuid",
  "threat_score": 85,
  "activity_type": "multiple_failed_logins"
}
```

---

## security.rate_limit.triggered

### Producer

API Gateway

### Consumers

* Audit Service

### Purpose

Track abusive request behavior.

---

# 5. Operational Events

## system.health.degraded

### Producer

Monitoring Service

### Consumers

* Alerting Service

### Purpose

Triggered when service health deteriorates.

---

## system.queue.backlog_detected

### Producer

RabbitMQ Monitoring

### Consumers

* Monitoring Service

### Purpose

Triggered when queue depth exceeds threshold.

---

# Retry Policy

## Retry Attempts

3 retries maximum.

## Retry Delays

* first retry: 5 seconds
* second retry: 30 seconds
* third retry: 2 minutes

---

# Dead Letter Queue Policy

## Conditions

Messages routed to DLQ when:

* validation fails
* retries exhausted
* malformed payloads detected

---

# Event Observability

## Logging

All events logged using structured JSON logging.

## Metrics

Prometheus metrics:

* event throughput
* consumer failures
* retry counts
* queue depth

## Tracing

OpenTelemetry correlation IDs required for all events.

---

# Future Enhancements

## Planned

* Kafka migration support
* schema registry
* event replay support
* distributed saga orchestration
