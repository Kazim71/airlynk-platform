"""
Tests for backend.shared.config.settings — Settings loading and validation.

Naming convention: test_<feature>_<scenario> (CODING_STANDARDS.md §13).
"""

from __future__ import annotations

import pytest

from backend.shared.config.settings import Environment, Settings


class TestSettingsDefaults:
    """Verify default configuration values load correctly."""

    def test_default_app_name(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            _env_file=None,
        )
        assert settings.app_name == "airlynk"

    def test_default_environment(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            _env_file=None,
        )
        assert settings.app_env == Environment.DEVELOPMENT

    def test_default_api_port(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            _env_file=None,
        )
        assert settings.api_port == 8000

    def test_default_access_token_expiry(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            _env_file=None,
        )
        assert settings.access_token_expire_minutes == 15

    def test_default_refresh_token_expiry(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            _env_file=None,
        )
        assert settings.refresh_token_expire_days == 7


class TestSettingsValidation:
    """Verify validation rules are enforced."""

    def test_invalid_log_level_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid log level"):
            Settings(
                jwt_secret="test-secret-at-least-16-chars",
                app_log_level="TRACE",
                _env_file=None,
            )

    def test_valid_log_levels_accepted(self) -> None:
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            settings = Settings(
                jwt_secret="test-secret-at-least-16-chars",
                app_log_level=level,
                _env_file=None,
            )
            assert settings.app_log_level == level

    def test_production_requires_strong_jwt_secret(self) -> None:
        with pytest.raises(ValueError, match="JWT_SECRET must be"):
            Settings(
                app_env="production",
                jwt_secret="short-but-16chars",  # ≥16 chars but <32 triggers model validator
                app_debug=False,
                _env_file=None,
            )

    def test_production_rejects_debug_mode(self) -> None:
        with pytest.raises(ValueError, match="APP_DEBUG must be false"):
            Settings(
                app_env="production",
                jwt_secret="a-very-long-secret-for-production-use-only-1234567890",
                app_debug=True,
                _env_file=None,
            )


class TestSettingsHelpers:
    """Verify derived properties."""

    def test_cors_origins_parsing(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            allowed_origins="http://localhost, http://example.com",
            _env_file=None,
        )
        assert settings.cors_origins == ["http://localhost", "http://example.com"]

    def test_is_production_flag(self) -> None:
        settings = Settings(
            app_env="production",
            jwt_secret="a-very-long-secret-for-production-use-only-1234567890",
            app_debug=False,
            _env_file=None,
        )
        assert settings.is_production is True
        assert settings.is_development is False

    def test_is_development_flag(self) -> None:
        settings = Settings(
            jwt_secret="test-secret-at-least-16-chars",
            app_env="development",
            _env_file=None,
        )
        assert settings.is_development is True
        assert settings.is_production is False
