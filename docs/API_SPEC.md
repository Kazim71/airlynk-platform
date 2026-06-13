# API_SPEC.md

# AirLynk API Specification

# Base URL

/api/v1/

---

# Authentication Standards

## Authentication Type

Bearer JWT Authentication

## Token Header

Authorization: Bearer <token>

---

# Standard Response Format

## Success Response

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

---

## Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": []
}
```

---

# 1. Authentication APIs

## POST /auth/register

### Description

Register new user account.

### Authentication

Public

### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

### Response

```json
{
  "success": true,
  "message": "User registered successfully"
}
```

---

## POST /auth/login

### Description

Authenticate user.

### Authentication

Public

### Request Body

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "access_token": "",
    "refresh_token": "",
    "expires_in": 900
  }
}
```

---

## POST /auth/refresh

### Description

Refresh access token.

### Authentication

Refresh Token Required

### Response

```json
{
  "success": true,
  "data": {
    "access_token": "",
    "refresh_token": ""
  }
}
```

---

## POST /auth/logout

### Description

Invalidate user session.

### Authentication

JWT Required

---

# 2. User APIs

## GET /users/me

### Description

Retrieve current user profile.

### Authentication

JWT Required

---

## PATCH /users/me

### Description

Update current user profile.

### Authentication

JWT Required

---

# 3. Booking APIs

## POST /bookings

### Description

Create booking.

### Authentication

Customer Role Required

### Request Body

```json
{
  "pickup_location": "",
  "dropoff_location": "",
  "scheduled_time": ""
}
```

---

## GET /bookings/{booking_id}

### Description

Retrieve booking details.

### Authentication

JWT Required

---

## PATCH /bookings/{booking_id}/status

### Description

Update booking status.

### Authentication

Driver or Operator Role Required

---

# 4. Admin APIs

## GET /admin/audit-logs

### Description

Retrieve audit logs.

### Authentication

Security Admin Role Required

---

## GET /admin/suspicious-activities

### Description

Retrieve suspicious activity records.

### Authentication

Security Admin Role Required

---

# 5. Health APIs

## GET /health

### Description

Service health check endpoint.

### Authentication

Public

---

## GET /metrics

### Description

Prometheus metrics endpoint.

### Authentication

Internal Only

---

# API Security Standards

## Request Validation

Pydantic schema validation mandatory.

## Rate Limiting

Redis sliding window algorithm.

## Content Type

application/json only.

## Maximum Payload Size

10 MB.

---

# HTTP Status Standards

| Status Code | Meaning               |
| ----------- | --------------------- |
| 200         | Success               |
| 201         | Created               |
| 400         | Bad Request           |
| 401         | Unauthorized          |
| 403         | Forbidden             |
| 404         | Not Found             |
| 409         | Conflict              |
| 422         | Validation Error      |
| 429         | Rate Limited          |
| 500         | Internal Server Error |

---

# API Versioning

Current Version:
v1

Future Strategy:
URI versioning using:
/api/v2/

---

# OpenAPI Standards

## Documentation

Swagger/OpenAPI auto-generated via FastAPI.

## Required Metadata

* endpoint descriptions
* request examples
* response examples
* authentication requirements
