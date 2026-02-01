"""API dependencies."""

from typing import Any, Dict

from litestar import Request
from litestar.di import Provide
from redis.asyncio import Redis

from backend.services.codeforces_data_service import CodeforcesDataService
from backend.domain.services.abandoned_problems_service import AbandonedProblemsService
from backend.domain.services.difficulty_distribution_service import DifficultyDistributionService
from backend.domain.services.tags_service import TagsService
from backend.infrastructure.task_queue import TaskQueue
from backend.infrastructure.redis_client import get_redis_client


def get_codeforces_data_service() -> CodeforcesDataService:
    """Dependency provider for CodeforcesDataService."""
    return CodeforcesDataService()


def get_abandoned_problems_service() -> AbandonedProblemsService:
    """Dependency provider for AbandonedProblemsService."""
    return AbandonedProblemsService()


def get_tags_service() -> TagsService:
    """Dependency provider for TagsService."""
    return TagsService()


def get_difficulty_distribution_service() -> DifficultyDistributionService:
    """Dependency provider for DifficultyDistributionService."""
    return DifficultyDistributionService()


async def get_redis() -> Redis:
    """Dependency provider for Redis client."""
    return await get_redis_client()


async def get_task_queue() -> TaskQueue:
    """Dependency provider for TaskQueue."""
    redis = await get_redis_client()
    return TaskQueue(redis)


def get_request_metadata(request: Request) -> Dict[str, Any]:
    """Extract metadata from the request."""
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip": request.client.host if request.client else None,
    }


# Dependency providers for route handlers
codeforces_data_service_dependency = Provide(get_codeforces_data_service, sync_to_thread=False)
abandoned_problems_service_dependency = Provide(
    get_abandoned_problems_service, sync_to_thread=False
)
difficulty_distribution_service_dependency = Provide(
    get_difficulty_distribution_service, sync_to_thread=False
)
tags_service_dependency = Provide(get_tags_service, sync_to_thread=False)
request_metadata_dependency = Provide(get_request_metadata, sync_to_thread=False)
redis_dependency = Provide(get_redis)
task_queue_dependency = Provide(get_task_queue)
