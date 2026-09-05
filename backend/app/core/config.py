from functools import lru_cache

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
    public_origin: str = Field(
        default="http://localhost:3000", validation_alias="VOLUMA_PUBLIC_ORIGIN"
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
