"""Abandoned problems API routes."""

from litestar import get
from litestar.response import Response

from backend.api.deps import (
    abandoned_problems_service_dependency,
    codeforces_data_service_dependency,
)
from backend.api.routes.base import BaseMetricController
from backend.api.schemas.abandoned_problems import (
    AbandonedProblemByRatingsResponse,
    AbandonedProblemByTagsResponse,
    RatingAbandonedSchema,
    TagAbandonedSchema,
)
from backend.domain.services.abandoned_problems_service import AbandonedProblemsService
from backend.services.codeforces_data_service import CodeforcesDataService


class AbandonedProblemsController(BaseMetricController):
    """Controller for abandoned problems endpoints."""

    path = "/abandoned-problems"
    tags = ["Abandoned Problems"]

    @get(
        path="/by-tags/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "abandoned_service": abandoned_problems_service_dependency,
        },
    )
    async def get_abandoned_problems_by_tags(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        abandoned_service: AbandonedProblemsService,
    ) -> Response[AbandonedProblemByTagsResponse]:
        """
        Get problems that user attempted but never solved, grouped by tags.

        Returns analysis of failed attempts across different topics. This helps identify
        weak areas where the user frequently struggles.

        Args:
            handle: Codeforces handle

        Returns:
            Abandoned problems analysis grouped by tags
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        analysis = abandoned_service.analyze_abandoned_problems(handle, submissions)

        tags = [
            TagAbandonedSchema(
                tag=tag_stats.tag,
                problem_count=tag_stats.problem_count,
                total_failed_attempts=tag_stats.total_failed_attempts,
            )
            for tag_stats in analysis.tags_stats
        ]

        response = AbandonedProblemByTagsResponse(
            tags=tags,
            total_abandoned_problems=analysis.total_abandoned,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)

    @get(
        path="/by-ratings/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "abandoned_service": abandoned_problems_service_dependency,
        },
    )
    async def get_abandoned_problems_by_ratings(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        abandoned_service: AbandonedProblemsService,
    ) -> Response[AbandonedProblemByRatingsResponse]:
        """
        Get problems that user attempted but never solved, grouped by rating bins.

        Shows the difficulty levels where user faces the most challenges and frequently
        abandons problems without solving them.

        Args:
            handle: Codeforces handle

        Returns:
            Abandoned problems analysis grouped by rating bins
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        analysis = abandoned_service.analyze_abandoned_problems(handle, submissions)

        ratings = [
            RatingAbandonedSchema(
                rating=rating_stats.rating,
                problem_count=rating_stats.problem_count,
                total_failed_attempts=rating_stats.total_failed_attempts,
            )
            for rating_stats in analysis.ratings_stats
        ]

        response = AbandonedProblemByRatingsResponse(
            ratings=ratings,
            total_abandoned_problems=analysis.total_abandoned,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)
