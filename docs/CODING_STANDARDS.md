# CODING_STANDARDS.md

# AirLynk Coding Standards

# 1. Engineering Philosophy

## Core Principles

* readability over cleverness
* security-first implementation
* strict typing everywhere
* modular architecture
* explicit over implicit behavior
* observability integrated by default

---

# 2. Python Standards

## Python Version

Python 3.12

## Mandatory Features

* type hints
* async/await for IO operations
* dataclass or Pydantic models where appropriate

---

# 3. Formatting Standards

## Formatter

Black

## Linter

Ruff

## Type Checker

mypy

---

# 4. Naming Conventions

# Variables

snake_case

Example:
user_id
booking_status

---

# Classes

PascalCase

Example:
AuthService
BookingRepository

---

# Constants

UPPER_SNAKE_CASE

Example:
ACCESS_TOKEN_EXPIRE_MINUTES

---

# File Names

snake_case.py

Example:
auth_service.py

---

# 5. Project Architecture

# Layered Architecture

## Layers

* API Layer
* Service Layer
* Repository Layer
* Infrastructure Layer

---

# API Layer Responsibilities

* request validation
* response formatting
* authentication middleware
* dependency injection

---

# Service Layer Responsibilities

* business logic
* orchestration
* transaction handling

---

# Repository Layer Responsibilities

* database interaction only
* no business logic

---

# Infrastructure Layer Responsibilities

* Redis
* RabbitMQ
* external services
* email integrations

---

# 6. FastAPI Standards

## API Prefix

/api/v1/

## Response Models

Mandatory for all endpoints.

## Dependency Injection

Use FastAPI dependency system only.

---

# 7. Pydantic Standards

## Validation

All request payloads validated using Pydantic v2.

## Forbidden

* raw dictionaries as request payloads
* manual payload validation

---

# 8. Database Standards

## ORM

SQLAlchemy 2.0

## Migrations

Alembic only.

## Query Standards

* parameterized queries only
* async database sessions

---

# 9. Logging Standards

## Logging Format

Structured JSON logs.

## Required Fields

* timestamp
* service_name
* request_id
* log_level
* message

---

# 10. Exception Handling

# Standard Error Response

```json id="ndzy0q"
{
  "success": false,
  "message": "Error message",
  "errors": []
}
```

---

# Forbidden

* silent exceptions
* broad exception swallowing
* print debugging

---

# 11. Security Standards

## Mandatory

* validate all inputs
* hash passwords using Argon2
* never expose internal errors
* audit security-sensitive actions

---

# Forbidden

* plaintext secrets
* hardcoded credentials
* inline SQL
* storing raw tokens

---

# 12. Async Standards

## Use Async For

* database operations
* HTTP requests
* Redis operations
* RabbitMQ operations

---

# Forbidden

Blocking operations inside async routes.

---

# 13. Testing Standards

## Minimum Coverage

80% minimum target.

## Test Types

* unit tests
* integration tests
* API tests

---

# Test Naming Convention

test_<feature>_<scenario>

Example:
test_login_invalid_password

---

# 14. Git Standards

## Commit Format

Examples:

* feat: implement JWT authentication
* fix: resolve Redis timeout issue
* refactor: simplify booking workflow

---

# 15. Documentation Standards

## Required

* docstrings for services
* OpenAPI descriptions
* README updates for major changes

---

# 16. Performance Standards

## Avoid

* N+1 queries
* unnecessary database calls
* synchronous blocking operations

---

# 17. Forbidden Patterns

## Strictly Forbidden

* fat controllers
* business logic inside routes
* direct DB access inside API handlers
* global mutable state
* hardcoded secrets

---

# 18. Future Standards

## Planned

* architecture decision records
* domain-driven design refinement
* internal package versioning
