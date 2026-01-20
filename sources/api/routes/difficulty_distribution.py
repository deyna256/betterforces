"""Difficulty distribution API routes."""

from litestar import get
from litestar.response import Response

from sources.api.deps import (
    codeforces_data_service_dependency,
    difficulty_distribution_service_dependency,
)
from sources.api.routes.base import BaseMetricController
from sources.api.schemas.difficulty_distribution import (
    DifficultyDistributionResponse,
    RatingRangeSchema,
)
from sources.domain.services.difficulty_distribution_service import DifficultyDistributionService
from sources.services.codeforces_data_service import CodeforcesDataService


class DifficultyDistributionController(BaseMetricController):
    """Controller for difficulty distribution endpoints."""

    path = "/difficulty-distribution"
    tags = ["Difficulty Distribution"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "difficulty_service": difficulty_distribution_service_dependency,
        },
    )
    async def get_difficulty_distribution(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        difficulty_service: DifficultyDistributionService,
    ) -> Response[DifficultyDistributionResponse]:
        """
        Get user's problem-solving distribution by difficulty levels.

        Returns statistics showing how many problems were solved in each
        rating bin (800, 900, 1000...). This helps identify comfort zones,
        practice gaps, and challenge areas.

        Args:
            handle: Codeforces handle

        Returns:
            Difficulty distribution analysis with rating bins and percentages
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        distribution = difficulty_service.analyze_difficulty_distribution(handle, submissions)

        ranges = [
            RatingRangeSchema(
                rating=range_data.rating,
                problem_count=range_data.problem_count,
            )
            for range_data in distribution.ranges
        ]

        response = DifficultyDistributionResponse(
            ranges=ranges,
            total_solved=distribution.total_solved,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)
