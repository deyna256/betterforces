"""Application configuration using Pydantic settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Development settings
    dev_mode: bool = Field(default=False, description="Enable development mode with hot reload")

    # Codeforces API settings
    codeforces_api_base: str = Field(
        default="https://codeforces.com/api", description="Base URL for Codeforces API"
    )

    # Cache settings
    cache_ttl: int = Field(
        default=4 * 60 * 60, description="Cache TTL in seconds (4 hours default)"
    )

    # Rate limiting settings
    rate_limit_requests: int = Field(
        default=100, description="Number of requests allowed per period"
    )
    rate_limit_period: Literal["second", "minute", "hour", "day"] = Field(
        default="hour", description="Rate limit period"
    )

    # User settings
    codeforces_user_handle: str = Field(
        default="", description="Default Codeforces user handle for testing"
    )

    # CORS settings
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
