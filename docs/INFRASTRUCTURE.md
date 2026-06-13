# INFRASTRUCTURE.md

# AirLynk Infrastructure Topology

# 1. Infrastructure Philosophy

## Core Goals

* containerized deployment
* cloud-native architecture
* security-first infrastructure
* observability-first operations
* horizontal scalability

---

# 2. Local Development Topology

# Docker Compose Services

| Service       | Purpose               |
| ------------- | --------------------- |
| nginx         | reverse proxy         |
| api           | FastAPI application   |
| postgres      | relational database   |
| redis         | cache and sessions    |
| rabbitmq      | message broker        |
| celery-worker | async task processing |
| prometheus    | metrics collection    |
| grafana       | dashboards            |
| loki          | centralized logging   |

---

# Local Request Flow

Client
↓
NGINX
↓
FastAPI Application
↓
PostgreSQL / Redis
↓
RabbitMQ
↓
Celery Workers

---

# 3. Reverse Proxy Layer

## Technology

NGINX

## Responsibilities

* TLS termination
* request routing
* security headers
* request size limiting
* rate limiting
* compression

---

# 4. Application Layer

## Runtime

Python 3.12

## Framework

FastAPI

## Deployment Style

Containerized stateless services.

---

# 5. Database Layer

## Primary Database

PostgreSQL 16

## Responsibilities

* transactional storage
* relational integrity
* indexing
* JSONB support

## Backup Strategy

Daily automated backups.

---

# 6. Cache Layer

## Technology

Redis 7

## Responsibilities

* session management
* refresh token storage
* rate limiting
* caching
* Celery backend

---

# 7. Messaging Layer

## Technology

RabbitMQ

## Responsibilities

* async communication
* event distribution
* retry handling
* dead-letter queues

---

# 8. Async Worker Layer

## Technology

Celery

## Responsibilities

* email processing
* background tasks
* retry orchestration
* delayed execution

---

# 9. Observability Stack

## Prometheus

Metrics collection.

## Grafana

Metrics visualization.

## Loki

Centralized structured logging.

## OpenTelemetry

Distributed tracing.

---

# 10. Cloud Deployment Architecture

# AWS Services

| AWS Service       | Purpose                 |
| ----------------- | ----------------------- |
| ECS Fargate       | container orchestration |
| RDS PostgreSQL    | managed database        |
| ElastiCache Redis | managed Redis           |
| CloudWatch        | cloud monitoring        |
| ECR               | container registry      |
| Secrets Manager   | secret storage          |
| IAM               | identity management     |
| WAF               | application firewall    |
| ALB               | load balancing          |

---

# AWS Deployment Flow

Internet
↓
AWS WAF
↓
Application Load Balancer
↓
ECS Fargate Services
↓
RDS / Redis / RabbitMQ

---

# 11. Networking Design

## VPC Structure

### Public Subnet

* load balancer
* NAT gateway

### Private Subnet

* ECS services
* PostgreSQL
* Redis
* RabbitMQ

---

# 12. Security Architecture

## Infrastructure Security Controls

### Network Security

* security groups
* restricted ingress
* private subnets

### Container Security

* non-root containers
* minimal base images
* image scanning

### Secret Management

AWS Secrets Manager.

---

# 13. Container Standards

## Base Image

python:3.12-slim

## Security Standards

* non-root execution
* read-only filesystem where possible
* pinned dependencies

---

# 14. Storage Strategy

## Persistent Storage

RDS PostgreSQL.

## Ephemeral Storage

Containers remain stateless.

---

# 15. Infrastructure as Code

## Technology

Terraform

## Managed Resources

* VPC
* ECS
* IAM
* Security Groups
* RDS
* Redis
* CloudWatch

---

# 16. Disaster Recovery

## Database Backups

Daily snapshots.

## Log Retention

30-day log retention minimum.

## Recovery Goal

Restore critical services within 1 hour.

---

# 17. Scalability Strategy

## Horizontal Scaling

ECS service auto-scaling.

## Stateless APIs

No session persistence inside containers.

## Queue-Based Load Handling

RabbitMQ absorbs traffic spikes.

---

# 18. Monitoring & Alerting

## Monitored Metrics

* API latency
* CPU usage
* memory usage
* queue backlog
* failed logins
* error rate

## Alert Conditions

* high API latency
* service downtime
* queue overload
* excessive auth failures

---

# 19. Future Infrastructure Enhancements

## Planned

* Kubernetes migration
* service mesh
* autoscaling policies
* blue-green deployment
* multi-region deployment
