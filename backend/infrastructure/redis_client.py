"""Redis client utilities for direct Redis access."""

from redis.asyncio import Redis

from backend.config import settings


async def create_redis_client() -> Redis:
    """
    Create a Redis client instance.

    Returns:
        Redis: Async Redis client
    """
    return Redis.from_url(settings.redis_url, decode_responses=False)


async def get_redis_client() -> Redis:
    """
    Get Redis client for dependency injection.

    This is a convenience function for DI in route handlers.

    Returns:
        Redis: Async Redis client instance
    """
    return await create_redis_client()
