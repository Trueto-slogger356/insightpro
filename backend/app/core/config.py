from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="postgresql+asyncpg://insightpro:insightpro@localhost:5432/insightpro")
    redis_url: str = Field(default="redis://localhost:6379/0")
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=480)
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")
    s3_bucket: str | None = None
    aws_region: str = "us-east-1"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
