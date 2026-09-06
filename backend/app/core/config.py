from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env", extra="ignore")

    environment: str = Field(default="development", validation_alias="VOLUMA_ENVIRONMENT")
    database_url: str = Field(
        default="postgresql+psycopg://voluma:voluma@localhost:5432/voluma",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", validation_alias="CELERY_BROKER_URL"
    )
    media_root: Path = Field(
        default=Path("/var/lib/voluma-media"), validation_alias="VOLUMA_MEDIA_ROOT"
    )
    public_origin: str = Field(
        default="http://localhost:3000", validation_alias="VOLUMA_PUBLIC_ORIGIN"
    )
    initial_admin_email: str | None = Field(
        default=None, validation_alias="VOLUMA_INITIAL_ADMIN_EMAIL"
    )
    initial_admin_password: str | None = Field(
        default=None, validation_alias="VOLUMA_INITIAL_ADMIN_PASSWORD"
    )
    admin_session_ttl_seconds: int = Field(
        default=8 * 60 * 60, validation_alias="VOLUMA_ADMIN_SESSION_TTL_SECONDS", ge=60
    )
    media_max_upload_bytes: int = Field(default=50 * 1024 * 1024, ge=1)
    media_max_dimension: int = Field(default=12_000, ge=1)
    media_max_pixels: int = Field(default=100_000_000, ge=1)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def admin_session_cookie_secure(self) -> bool:
        """Require HTTPS session cookies outside the explicitly local development mode."""

        return self.is_production


@lru_cache
def get_settings() -> Settings:
    return Settings()
