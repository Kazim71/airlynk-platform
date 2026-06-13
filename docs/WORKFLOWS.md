# WORKFLOWS.md

# AirLynk Workflow Specification

## 1. Authentication Login Workflow

### Objective

Authenticate users securely while enforcing audit logging, MFA, and anomaly detection.

---

## Login Flow Sequence

1. Client submits login request.
2. API Gateway validates request format.
3. Auth Service validates credentials against PostgreSQL.
4. Password verified using Argon2 hash comparison.
5. Redis rate-limit check performed.
6. MFA verification triggered if enabled.
7. JWT access token generated.
8. Refresh token generated and stored in Redis.
9. Session metadata stored:

   * IP address
   * device fingerprint
   * login timestamp
10. Audit event published to RabbitMQ.
11. Audit Service consumes event and stores immutable log.
12. Metrics updated in Prometheus.
13. Response returned to client.

---

## Login Failure Workflow

1. Failed password attempt detected.
2. Failure counter incremented in Redis.
3. Suspicious activity score recalculated.
4. Audit event emitted.
5. Temporary lock applied after threshold exceeded.
6. Alert metrics updated.

---

# 2. Refresh Token Workflow

## Objective

Maintain secure session continuity using rotating refresh tokens.

---

## Refresh Sequence

1. Client submits refresh token.
2. Redis validates token existence.
3. Token expiration validated.
4. Previous refresh token invalidated.
5. New access token generated.
6. New refresh token generated.
7. New refresh token stored in Redis.
8. Audit event published.
9. Response returned.

---

# 3. Logout Workflow

## Objective

Invalidate user session securely.

---

## Logout Sequence

1. Client submits logout request.
2. Access token validated.
3. Refresh token deleted from Redis.
4. Session invalidated.
5. Audit event generated.
6. User logged out successfully.

---

# 4. Booking Creation Workflow

## Objective

Create bookings while maintaining transactional consistency.

---

## Booking Flow

1. Customer submits booking request.
2. API Gateway validates JWT.
3. Booking Service validates payload.
4. Pricing engine calculates estimated fare.
5. Booking persisted in PostgreSQL.
6. Booking event published to RabbitMQ.
7. Notification Service consumes event.
8. Confirmation email queued.
9. Audit log event generated.
10. Metrics updated.

---

# 5. Driver Assignment Workflow

## Objective

Assign drivers asynchronously.

---

## Assignment Flow

1. Booking enters pending state.
2. Dispatch engine searches available drivers.
3. Driver assignment algorithm executed.
4. Driver notified asynchronously.
5. Booking status updated.
6. Assignment audit event generated.

---

# 6. Notification Workflow

## Objective

Handle asynchronous notifications.

---

## Email Notification Flow

1. Event received from RabbitMQ.
2. Celery worker processes task.
3. Email template rendered using Jinja2.
4. SMTP service sends email.
5. Delivery status logged.
6. Failure retries triggered if needed.

---

# 7. Suspicious Activity Workflow

## Objective

Detect abnormal authentication behavior.

---

## Detection Triggers

* repeated failed logins
* unusual geographic access
* impossible travel detection
* multiple device logins
* token abuse patterns

---

## Detection Sequence

1. Event consumed from RabbitMQ.
2. Threat score calculated.
3. Redis temporary risk profile updated.
4. Alert threshold evaluated.
5. Security event stored.
6. Alert dashboard updated.

---

# 8. Audit Logging Workflow

## Objective

Ensure immutable security event traceability.

---

## Audit Event Flow

1. Service emits audit event.
2. RabbitMQ routes event.
3. Audit Service consumes event.
4. Event validated.
5. Immutable audit record stored.
6. Loki structured log emitted.
7. Metrics updated.

---

# 9. Health Monitoring Workflow

## Objective

Maintain platform observability.

---

## Monitoring Flow

1. Prometheus scrapes service metrics.
2. Grafana dashboards visualize metrics.
3. Alert rules evaluated.
4. Critical alerts routed.
5. Logs centralized in Loki.
6. Traces correlated via OpenTelemetry.
