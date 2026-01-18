"""Litestar application configuration."""

from litestar import Litestar
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.memory import MemoryStore

# TODO: Add Redis support when infrastructure is ready
# from litestar.contrib.redis import RedisStore

from sources.api.routes import routes
from sources.config import settings


def create_app() -> Litestar:
    """Create and configure the Litestar application."""

    # Configure stores (using MemoryStore for MVP)
    stores = {
        "default": MemoryStore(),
        "rate_limit": MemoryStore(),
    }

    # Configure rate limiting
    rate_limit_config = RateLimitConfig(
        rate_limit=(settings.rate_limit_period, settings.rate_limit_requests),
        store="rate_limit",
        exclude=["/schema"],  # Exclude OpenAPI schema endpoint
    )

    return Litestar(
        route_handlers=routes,
        stores=stores,
        middleware=[rate_limit_config.middleware],
        openapi_config=OpenAPIConfig(
            title="BetterForces API",
            version="1.0.0",
            description="API for Codeforces profile analysis",
        ),
    )