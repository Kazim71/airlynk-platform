# AirLynk - Technical Architecture Specification

# 1. Architecture Style

## Primary Style

Modular Monolith with Microservice Boundaries

## Reasoning

Chosen to:

* reduce operational complexity
* simplify local development
* preserve clean service boundaries
* support future service extraction

---

# 2. High-Level Architecture

Client Layer
↓
NGINX Reverse Proxy
↓
API Gateway Layer
↓
Application Services
↓
Infrastructure Layer

---

# 3. Technology Stack

## Backend Framework

### FastAPI

Purpose:

* async APIs
* OpenAPI generation
* modern typing
* high performance

Version:

* Python 3.12
* FastAPI latest stable

---

# 4. Service Modules

## 4.1 Auth Service

### Responsibilities

* authentication
* authorization
* MFA
* token lifecycle
* session management

### Stack

* FastAPI
* PostgreSQL
* Redis

### Libraries

* Pydantic v2
* SQLAlchemy 2.0
* Alembic
* Passlib
* PyJWT
* python-jose
* pyotp

---

## 4.2 Booking Service

### Responsibilities

* booking lifecycle
* trip state management
* pricing logic

### Stack

* FastAPI
* PostgreSQL

---

## 4.3 Notification Service

### Responsibilities

* email notifications
* async event handling
* webhook dispatch

### Stack

* Celery
* RabbitMQ
* Redis

### Libraries

* Celery
* aio-pika
* Jinja2
* aiosmtplib

---

## 4.4 Audit Service

### Responsibilities

* immutable audit logging
* threat scoring
* suspicious activity tracking

### Stack

* PostgreSQL
* Redis

---

# 5. Infrastructure Stack

## Reverse Proxy

### NGINX

Purpose:

* reverse proxy
* TLS termination
* request filtering
* rate limiting

---

## Database

### PostgreSQL 16

Purpose:

* transactional storage
* relational integrity
* indexing
* JSONB support

---

## Cache Layer

### Redis 7

Purpose:

* caching
* rate limiting
* session storage
* Celery broker

---

## Message Queue

### RabbitMQ

Purpose:

* event-driven communication
* async task dispatch

---

# 6. Observability Stack

## Metrics

### Prometheus

Collect:

* request counts
* latency
* CPU/memory metrics
* queue metrics

---

## Dashboards

### Grafana

Dashboards:

* API latency
* auth failures
* queue depth
* suspicious activity

---

## Logging

### Loki

Centralized structured logs.

---

## Distributed Tracing

### OpenTelemetry

Trace:

* request flow
* DB calls
* async workflows

---

# 7. DevOps Stack

## Containerization

### Docker

### Docker Compose

---

## CI/CD

### GitHub Actions

Pipeline stages:

1. lint
2. test
3. security scan
4. build
5. deploy

---

## Security Scanning

### Bandit

Python security scanning

### Semgrep

Static analysis

### Trivy

Container vulnerability scanning

### Safety

Dependency vulnerability scanning

---

# 8. Cloud Stack

## Cloud Provider

AWS

## Planned Services

### Compute

* ECS Fargate initially
* EKS optional later

### Database

* Amazon RDS PostgreSQL

### Cache

* ElastiCache Redis

### Monitoring

* CloudWatch

### Security

* IAM
* Security Groups
* AWS WAF
* Secrets Manager

---

# 9. Infrastructure as Code

## Terraform

Purpose:

* VPC
* ECS
* RDS
* IAM
* Security Groups
* networking

---

# 10. API Standards

## API Style

RESTful APIs

## Documentation

OpenAPI/Swagger

## Authentication

Bearer JWT

## Versioning

/api/v1/

---

# 11. Coding Standards

## Formatting

* Ruff
* Black

## Typing

* strict typing mandatory

## Architecture

* service-repository pattern
* dependency injection
* layered architecture

---

# 12. Testing Strategy

## Unit Testing

Pytest

## Integration Testing

Testcontainers

## API Testing

HTTPX

## Load Testing

k6

---

# 13. Directory Structure

backend/
├── services/
│   ├── auth/
│   ├── booking/
│   ├── notification/
│   ├── audit/
│
├── shared/
│   ├── security/
│   ├── middleware/
│   ├── logging/
│   ├── observability/
│   └── events/
│
├── infrastructure/
│   ├── docker/
│   ├── terraform/
│   ├── nginx/
│   └── github-actions/
│
├── observability/
│   ├── grafana/
│   ├── prometheus/
│   └── loki/
│
└── docs/
