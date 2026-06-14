"""
Tests for backend.shared.schemas.responses — API response schemas.
"""

from __future__ import annotations

from backend.shared.schemas.responses import ErrorResponse, HealthStatus, SuccessResponse


class TestSuccessResponse:
    """Verify the standard success response format."""

    def test_default_success_response(self) -> None:
        resp = SuccessResponse[None]()
        assert resp.success is True
        assert resp.message == "Request successful"
        assert resp.data is None

    def test_success_response_with_data(self) -> None:
        data = {"user_id": "123", "email": "test@example.com"}
        resp = SuccessResponse[dict](data=data, message="User retrieved")
        assert resp.success is True
        assert resp.data == data

    def test_success_response_json(self) -> None:
        resp = SuccessResponse[str](data="hello", message="OK")
        json_data = resp.model_dump()
        assert json_data["success"] is True
        assert json_data["data"] == "hello"


class TestErrorResponse:
    """Verify the standard error response format."""

    def test_default_error_response(self) -> None:
        resp = ErrorResponse()
        assert resp.success is False
        assert resp.errors == []

    def test_error_response_with_errors(self) -> None:
        errors = [{"field": "email", "message": "Invalid email format"}]
        resp = ErrorResponse(message="Validation failed", errors=errors)
        assert resp.success is False
        assert resp.message == "Validation failed"
        assert len(resp.errors) == 1

    def test_error_response_json(self) -> None:
        resp = ErrorResponse(message="Not found")
        json_data = resp.model_dump()
        assert json_data["success"] is False
        assert json_data["message"] == "Not found"


class TestHealthStatus:
    """Verify the health status response model."""

    def test_healthy_status(self) -> None:
        health = HealthStatus(status="healthy", postgres=True, redis=True, rabbitmq=True)
        assert health.status == "healthy"
        assert health.postgres is True

    def test_degraded_status(self) -> None:
        health = HealthStatus(status="degraded", postgres=True, redis=False, rabbitmq=True)
        assert health.status == "degraded"
        assert health.redis is False
