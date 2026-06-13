# SERVICE_TEMPLATE.md

# AirLynk Service Template Standard

# 1. Purpose

This document defines the standard structure for all backend services inside AirLynk.

All services must follow the same architecture, naming conventions, and dependency patterns.

---

# 2. Standard Service Structure

service-name/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── security/
│   │   ├── logging/
│   │   └── observability/
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── events/
│   ├── middleware/
│   ├── workers/
│   └── main.py
│
├── tests/
├── alembic/
├── Dockerfile
├── requirements.txt
└── pyproject.toml

---

# 3. API Layer Standards

# Responsibilities

* request validation
* authentication
* response formatting
* dependency injection

---

# Forbidden

* business logic
* direct DB queries

---

# 4. Service Layer Standards

# Responsibilities

* business workflows
* orchestration
* transaction management

---

# Forbidden

* raw HTTP request handling
* response serialization

---

# 5. Repository Layer Standards

# Responsibilities

* database access only
* ORM query handling

---

# Forbidden

* business rules
* external API calls

---

# 6. Schema Standards

# Technology

Pydantic v2

# Required Schemas

* request schemas
* response schemas
* internal DTOs

---

# 7. Configuration Standards

# Configuration Source

Environment variables only.

# Validation

Pydantic Settings.

---

# 8. Logging Standards

# Required Logger Context

* request_id
* service_name
* trace_id

---

# 9. Health Check Standards

# Required Endpoints

## /health

basic service health.

## /ready

service readiness validation.

---

# 10. Database Standards

# ORM

SQLAlchemy 2.0

# Migration Tool

Alembic

# Session Strategy

async sessions only.

---

# 11. Event Standards

# Event Broker

RabbitMQ

# Event Format

JSON event envelope.

---

# 12. Testing Standards

# Required Tests

* unit tests
* API tests
* repository tests

---

# 13. Docker Standards

# Requirements

* non-root execution
* slim images
* health checks

---

# 14. Security Standards

# Mandatory

* input validation
* RBAC enforcement
* audit logging

---

# 15. Observability Standards

# Required

* Prometheus metrics
* structured logs
* OpenTelemetry tracing

---

# 16. Future Enhancements

## Planned

* internal SDK packages
* shared event contracts
* service discovery
