"""
AirLynk — Centralized Application Settings.

All configuration is loaded from environment variables and validated at startup
using Pydantic Settings.  See SERVICE_TEMPLATE.md §7 and CODING_STANDARDS.md §7.

Environment files:
  .env.development   — local Docker Compose stack
  .env.staging       — staging environment
  .env.production    — production environment
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Immutable, validated application configuration loaded from env vars."""

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application -----------------------------------------------------------
    app_name: str = Field(default="airlynk", description="Service name for logs & traces")
    app_env: Environment = Field(default=Environment.DEVELOPMENT)
    app_debug: bool = Field(default=False)
    app_log_level: str = Field(default="INFO")

    # --- FastAPI ---------------------------------------------------------------
    api_host: str = Field(default="0.0.0.0")  # noqa: S104
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_workers: int = Field(default=1, ge=1)
    allowed_origins: str = Field(
        default="http://localhost",
        description="Comma-separated CORS origins",
    )

    # --- PostgreSQL ------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://airlynk:airlynk_dev_password@localhost:5432/airlynk",
    )
    database_pool_size: int = Field(default=10, ge=1)
    database_max_overflow: int = Field(default=20, ge=0)

    # --- Redis -----------------------------------------------------------------
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- RabbitMQ --------------------------------------------------------------
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/")

    # --- JWT -------------------------------------------------------------------
    jwt_secret: str = Field(
        default="CHANGE_ME",
        min_length=16,
        description="HMAC signing key — must be ≥ 32 chars in production",
    )
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)

    # --- SMTP ------------------------------------------------------------------
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_username: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from_email: str = Field(default="noreply@airlynk.dev")

    # --- OpenTelemetry ---------------------------------------------------------
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str = Field(default="airlynk-api")

    # --- AWS -------------------------------------------------------------------
    aws_region: str = Field(default="us-east-1")

    # --- Derived helpers -------------------------------------------------------

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.app_env == Environment.DEVELOPMENT

    # --- Validators ------------------------------------------------------------

    @field_validator("app_log_level")
    @classmethod
    def _normalise_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            msg = f"Invalid log level '{v}'. Must be one of {allowed}"
            raise ValueError(msg)
        return upper

    @model_validator(mode="after")
    def _validate_production_constraints(self) -> Settings:
        """Enforce stricter rules when running in production."""
        if self.is_production:
            if self.jwt_secret == "CHANGE_ME" or len(self.jwt_secret) < 32:
                msg = "JWT_SECRET must be ≥ 32 characters in production"
                raise ValueError(msg)
            if self.app_debug:
                msg = "APP_DEBUG must be false in production"
                raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Module-level singleton — import ``get_settings`` for DI, never instantiate
# ``Settings()`` directly in service code.
# ---------------------------------------------------------------------------
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def override_settings(overrides: dict[str, Any]) -> Settings:
    """Create a new Settings instance with overrides — used only in tests."""
    global _settings
    _settings = Settings(**overrides)
    return _settings
