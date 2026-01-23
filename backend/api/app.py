"""Litestar application configuration."""

import logging

from litestar import Litestar, Router
from litestar.config.cors import CORSConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.redis import RedisStore

from backend.api.routes import routes
from backend.config import settings


def create_app() -> Litestar:
    """Create and configure the Litestar application."""

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Configure stores (using RedisStore for production caching)
    stores = {
        "default": RedisStore.with_client(url=settings.redis_url),
        "rate_limit": RedisStore.with_client(url=settings.redis_url),
    }

    # Configure rate limiting
    rate_limit_config = RateLimitConfig(
        rate_limit=(settings.rate_limit_period, settings.rate_limit_requests),
        store="rate_limit",
        exclude=["/schema"],  # Exclude OpenAPI schema endpoint
    )

    # Configure CORS
    cors_config = CORSConfig(
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Create API router with /api prefix
    api_router = Router(path="/api", route_handlers=routes)

    return Litestar(
        route_handlers=[api_router],
        stores=stores,
        cors_config=cors_config,
        middleware=[rate_limit_config.middleware],
        openapi_config=OpenAPIConfig(
            title="BetterForces API",
            version="1.0.0",
            description="API for Codeforces profile analysis",
            root_schema_site="element",
        ),
    )
