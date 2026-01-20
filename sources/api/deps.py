"""API dependencies."""

from typing import Any, Dict

from litestar import Request
from litestar.di import Provide

from sources.services.codeforces_data_service import CodeforcesDataService
from sources.domain.services.abandoned_problems_service import AbandonedProblemsService
from sources.domain.services.difficulty_distribution_service import DifficultyDistributionService
from sources.domain.services.difficulty_progression_service import DifficultyProgressionService
from sources.domain.services.rating_distribution_service import RatingDistributionService
from sources.domain.services.tags_service import TagsService


def get_codeforces_data_service() -> CodeforcesDataService:
    """Dependency provider for CodeforcesDataService."""
    return CodeforcesDataService()


def get_abandoned_problems_service() -> AbandonedProblemsService:
    """Dependency provider for AbandonedProblemsService."""
    return AbandonedProblemsService()


def get_rating_distribution_service() -> RatingDistributionService:
    """Dependency provider for RatingDistributionService."""
    return RatingDistributionService()


def get_difficulty_progression_service() -> DifficultyProgressionService:
    """Dependency provider for DifficultyProgressionService."""
    return DifficultyProgressionService()


def get_tags_service() -> TagsService:
    """Dependency provider for TagsService."""
    return TagsService()


def get_difficulty_distribution_service() -> DifficultyDistributionService:
    """Dependency provider for DifficultyDistributionService."""
    return DifficultyDistributionService()


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
difficulty_progression_service_dependency = Provide(
    get_difficulty_progression_service, sync_to_thread=False
)
rating_distribution_service_dependency = Provide(
    get_rating_distribution_service, sync_to_thread=False
)
tags_service_dependency = Provide(get_tags_service, sync_to_thread=False)
request_metadata_dependency = Provide(get_request_metadata, sync_to_thread=False)
