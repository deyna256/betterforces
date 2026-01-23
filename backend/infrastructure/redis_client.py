"""Redis client for BetterForces."""

import redis.asyncio as redis
from typing import Optional
from backend.config import settings


class RedisClient:
    """Async Redis client for caching."""

    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 0) -> bool:
        """
        Set value in Redis with optional TTL.

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (0 means no expiration)

        Returns:
            True if successful
        """
        if ttl > 0:
            return bool(await self.redis.setex(key, ttl, value))
        else:
            return bool(await self.redis.set(key, value))

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        return bool(await self.redis.delete(key))

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return bool(await self.redis.exists(key))

    async def close(self):
        """Close Redis connection."""
        await self.redis.close()
