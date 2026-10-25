"""Application settings loaded from environment variables / .env files.

Database connection strategy
----------------------------
``DATABASE_URL`` is the single source of truth for the database connection.
It always uses the asynchronous ``postgresql+asyncpg`` driver so the FastAPI
application and the Alembic migrations can never drift apart - both read the
very same value from this module.

For convenience the discrete variables ``DB_HOST`` / ``DB_PORT`` / ``DB_USER``
/ ``DB_PASSWORD`` / ``DB_NAME`` are also supported: when ``DATABASE_URL`` is
not provided the URL is composed from them.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration object.

    All values can be overridden through environment variables (or a ``.env``
    file). Field names are matched case-insensitively.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -- Application -----------------------------------------------------
    app_name: str = "JapanToGo API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # -- Database --------------------------------------------------------
    # Full connection string. Preferred over the discrete DB_* variables.
    database_url: str = ""

    # Discrete connection components, used to compose ``database_url`` when it
    # is not explicitly provided.
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "japantogo"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_echo: bool = False

    # -- Security --------------------------------------------------------
    # ``JWT_SECRET`` is the canonical name; ``SECRET_KEY`` is kept as an alias.
    jwt_secret: str = Field(
        default="dev-secret-key-change-me-0123456789abcdef",
        validation_alias=AliasChoices("jwt_secret", "secret_key"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # Session cookies. Both tokens travel exclusively in HttpOnly cookies so
    # that no script running in the browser can ever read them.
    access_token_cookie_name: str = "access_token"
    refresh_token_cookie_name: str = "refresh_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_domain: str | None = None

    # Password policy
    password_min_length: int = 8
    password_max_length: int = 128

    # -- Rate limiting ---------------------------------------------------
    rate_limit_enabled: bool = True
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"
    rate_limit_calculator: str = "30/minute"
    rate_limit_storage_uri: str = "memory://"

    # -- CORS ------------------------------------------------------------
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # -- Storage ---------------------------------------------------------
    uploads_dir: str = "uploads"
    max_upload_size_mb: int = 5
    max_inspection_photos: int = 5
    image_max_width: int = 1920
    image_max_height: int = 1080
    image_quality: int = 85
    allowed_image_types: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp"]
    )
    allowed_receipt_types: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf",
        ]
    )

    # -- Business rules --------------------------------------------------
    service_fee_rate: float = 0.20
    service_fee_min_jpy: int = 2_000
    service_fee_floor_threshold_jpy: int = 10_000

    # -- Landed cost simulator ------------------------------------------
    jpy_to_brl_rate: float = 0.038
    exchange_rate_spread: float = 0.02
    rts_rate: float = 0.60
    icms_rate: float = 0.18
    ems_base_jpy: int = 3_000
    ems_per_500g_jpy: int = 600
    small_packet_base_jpy: int = 1_500
    small_packet_per_500g_jpy: int = 300
    small_packet_max_grams: int = 2_000

    # -- Legal -----------------------------------------------------------
    terms_version: str = "1.0.0"
    privacy_version: str = "1.0.0"

    # -- Validators ------------------------------------------------------
    @field_validator(
        "cors_origins",
        "allowed_image_types",
        "allowed_receipt_types",
        mode="before",
    )
    @classmethod
    def _split_csv(cls, value: object) -> object:
        """Allow comma separated environment variables for list settings."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cookie_domain", mode="before")
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        """Treat an empty string as "not set"."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def _resolve_database_url(self) -> "Settings":
        """Ensure ``database_url`` is set and always uses the async driver."""
        if not self.database_url:
            self.database_url = self._compose_database_url()
        else:
            self.database_url = self._normalise_driver(self.database_url)
        return self

    def _compose_database_url(self) -> str:
        from urllib.parse import quote_plus

        user = quote_plus(self.db_user)
        password = f":{quote_plus(self.db_password)}" if self.db_password else ""
        return (
            f"postgresql+asyncpg://{user}{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @staticmethod
    def _normalise_driver(url: str) -> str:
        """Force the asyncpg driver even if a sync URL was supplied.

        Alembic accepts both forms, but the application is fully async, so the
        URL is upgraded to ``postgresql+asyncpg://`` for consistency.
        """
        if url.startswith("postgresql+"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # -- Helpers ---------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
