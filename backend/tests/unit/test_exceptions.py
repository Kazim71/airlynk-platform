"""
Tests for backend.shared.exceptions.handlers — Exception hierarchy.
"""

from __future__ import annotations

from backend.shared.exceptions.handlers import (
    AirLynkError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Verify the exception hierarchy and HTTP status code mapping."""

    def test_base_error_defaults(self) -> None:
        exc = AirLynkError()
        assert exc.status_code == 500
        assert exc.message == "Internal server error"
        assert exc.errors == []

    def test_base_error_custom_message(self) -> None:
        exc = AirLynkError(message="Something went wrong", errors=["detail"])
        assert exc.message == "Something went wrong"
        assert exc.errors == ["detail"]

    def test_not_found_error(self) -> None:
        exc = NotFoundError()
        assert exc.status_code == 404
        assert exc.message == "Resource not found"

    def test_authentication_error(self) -> None:
        exc = AuthenticationError(message="Invalid token")
        assert exc.status_code == 401
        assert exc.message == "Invalid token"

    def test_authorization_error(self) -> None:
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert exc.message == "Permission denied"

    def test_validation_error(self) -> None:
        exc = ValidationError(errors=["email is required"])
        assert exc.status_code == 422
        assert "email is required" in exc.errors

    def test_conflict_error(self) -> None:
        exc = ConflictError(message="User already exists")
        assert exc.status_code == 409

    def test_rate_limit_error(self) -> None:
        exc = RateLimitError()
        assert exc.status_code == 429

    def test_all_exceptions_inherit_from_base(self) -> None:
        exceptions = [
            NotFoundError,
            AuthenticationError,
            AuthorizationError,
            ValidationError,
            ConflictError,
            RateLimitError,
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, AirLynkError)
            assert issubclass(exc_class, Exception)
