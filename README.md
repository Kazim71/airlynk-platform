# AirLynk

> Cloud-native secure backend platform built with FastAPI, PostgreSQL, Redis, RabbitMQ, and a full observability stack.

---

## Architecture

AirLynk follows a **modular monolith with microservice boundaries** pattern, using layered architecture (API → Service → Repository → Infrastructure) with strict separation of concerns.

| Layer            | Technology                     |
|------------------|--------------------------------|
| API Framework    | FastAPI (Python 3.12)          |
| Database         | PostgreSQL 16 + SQLAlchemy 2.0 |
| Cache            | Redis 7                       |
| Message Broker   | RabbitMQ                       |
| Task Queue       | Celery                         |
| Reverse Proxy    | NGINX                          |
| Metrics          | Prometheus                     |
| Dashboards       | Grafana                        |
| Logging          | Loki + structlog               |
| Tracing          | OpenTelemetry                  |
| IaC              | Terraform                      |
| CI/CD            | GitHub Actions                 |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development without Docker)

### Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/airlynk.git
cd airlynk

# Start all services
docker compose --env-file .env.development up --build -d

# Verify health
curl http://localhost/health

# View logs
docker compose logs -f api
```

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Run API server
uvicorn backend.services.api.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
pytest backend/tests/ -v
```

### Linting & Formatting

```bash
ruff check backend/
black --check backend/
mypy backend/
```

## Repository Structure

```
backend/
├── services/           # Service modules
│   ├── api/            # FastAPI application
│   └── worker/         # Celery workers
├── shared/             # Shared core packages
│   ├── config/         # Pydantic Settings
│   ├── database/       # SQLAlchemy async sessions
│   ├── cache/          # Redis client
│   ├── messaging/      # RabbitMQ client
│   ├── events/         # Event envelope models
│   ├── schemas/        # Shared response schemas
│   ├── exceptions/     # Exception hierarchy
│   ├── security/       # JWT, password hashing
│   ├── middleware/     # Correlation ID, RBAC, security headers
│   ├── logging/        # Structured JSON logging
│   └── observability/  # OpenTelemetry, Prometheus
├── tests/              # Test suite
├── alembic/            # Database migrations
└── Dockerfile          # Multi-stage container build

infrastructure/
├── nginx/              # Reverse proxy configuration
└── terraform/          # Infrastructure as Code

observability/
├── prometheus/         # Metrics collection config
├── grafana/            # Dashboard provisioning
└── loki/               # Log aggregation config

docs/                   # Architecture specifications
```

## Engineering Standards

- **Strict typing** everywhere — enforced by mypy
- **Async-first** — all I/O operations use async/await
- **Repository pattern** — no direct DB access in routes
- **Structured JSON logging** — with correlation IDs
- **Security-first** — Argon2 hashing, JWT rotation, RBAC, security headers
- **Observability-first** — OpenTelemetry tracing, Prometheus metrics, Loki logs

## Documentation

All architecture decisions and engineering standards are documented in the [`docs/`](docs/) directory.

## License

MIT
