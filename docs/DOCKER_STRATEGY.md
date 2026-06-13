# DOCKER_STRATEGY.md

# AirLynk Docker Strategy

# 1. Containerization Philosophy

## Goals

* reproducible environments
* isolated services
* stateless application containers
* security-first container design
* simplified local development

---

# 2. Container Standards

## Base Image

### Approved Base Image

python:3.12-slim

### Reasoning

* minimal attack surface
* reduced image size
* faster deployment
* lower dependency footprint

---

# 3. Security Standards

## Mandatory Requirements

### Non-Root User

All containers must run using non-root users.

### Dependency Pinning

All dependencies must use pinned versions.

### Minimal Layers

Optimize Dockerfile layers for smaller image size.

### Read-Only Filesystem

Use read-only containers where applicable.

### No Secrets in Images

Secrets must never exist inside Docker images.

---

# 4. Service Containers

# API Container

## Responsibilities

* FastAPI runtime
* API request handling
* JWT authentication
* business logic execution

## Exposed Port

8000

---

# PostgreSQL Container

## Responsibilities

* persistent relational storage

## Exposed Port

5432

## Persistence

Docker volume mounted.

---

# Redis Container

## Responsibilities

* session storage
* caching
* rate limiting
* Celery backend

## Exposed Port

6379

---

# RabbitMQ Container

## Responsibilities

* event distribution
* async messaging

## Exposed Ports

5672
15672

---

# Celery Worker Container

## Responsibilities

* background task processing
* email delivery
* retries
* event processing

---

# Prometheus Container

## Responsibilities

* metrics collection

## Exposed Port

9090

---

# Grafana Container

## Responsibilities

* observability dashboards

## Exposed Port

3000

---

# Loki Container

## Responsibilities

* centralized logging

## Exposed Port

3100

---

# NGINX Container

## Responsibilities

* reverse proxy
* request routing
* TLS termination
* security headers

## Exposed Ports

80
443

---

# 5. Docker Networking Strategy

## Network Name

airlynk-network

## Communication Rules

* internal services communicate using Docker DNS
* only NGINX exposed publicly
* PostgreSQL isolated internally
* Redis isolated internally

---

# 6. Volume Strategy

## Persistent Volumes

### postgres-data

Stores PostgreSQL data.

### rabbitmq-data

Stores RabbitMQ queues.

### grafana-data

Stores dashboard configuration.

---

# 7. Environment Configuration

## Local Environment Files

### Files

* .env.development
* .env.staging
* .env.production

## Prohibited

* committing secrets to git
* plaintext credentials in repositories

---

# 8. Docker Compose Strategy

## Compose Profiles

### development

local development stack.

### observability

monitoring stack only.

### production

production-aligned local simulation.

---

# 9. Build Strategy

## Multi-Stage Builds

### Stage 1

Dependency installation.

### Stage 2

Minimal runtime image creation.

---

# 10. Health Checks

## Mandatory Health Endpoints

### API

/health

### PostgreSQL

pg_isready

### Redis

redis-cli ping

### RabbitMQ

management health endpoint

---

# 11. Logging Standards

## Log Format

Structured JSON logs.

## Log Targets

stdout/stderr only.

---

# 12. Resource Constraints

## API Container

* CPU limit
* memory limit

## Worker Container

separate scaling configuration.

---

# 13. Image Naming Convention

## Format

airlynk/<service-name>:<version>

Examples:

* airlynk/api:v1.0.0
* airlynk/worker:v1.0.0

---

# 14. Local Development Workflow

## Startup Sequence

1. PostgreSQL
2. Redis
3. RabbitMQ
4. API
5. Workers
6. Observability stack

---

# 15. Future Enhancements

## Planned

* Kubernetes manifests
* Helm charts
* service mesh integration
* autoscaling support
