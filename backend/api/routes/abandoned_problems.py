"""Abandoned problems API routes."""

import asyncio

from litestar import get
from litestar.params import Parameter
from litestar.response import Response
from litestar.exceptions import HTTPException
from redis.asyncio import Redis

from backend.api.deps import (
    abandoned_problems_service_dependency,
    codeforces_data_service_dependency,
    redis_dependency,
    task_queue_dependency,
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
from backend.infrastructure.codeforces_client import UserNotFoundError
from backend.infrastructure.task_queue import TaskQueue


class AbandonedProblemsController(BaseMetricController):
    """Controller for abandoned problems endpoints."""

    path = "/abandoned-problems"
    tags = ["Abandoned Problems"]

    @get(
        path="/by-tags/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "abandoned_service": abandoned_problems_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_abandoned_problems_by_tags(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        abandoned_service: AbandonedProblemsService,
        redis: Redis,
        task_queue: TaskQueue,
        prefer_fresh: bool = Parameter(
            default=False,
            description="If true, force refresh even if stale data is available",
        ),
    ) -> Response[AbandonedProblemByTagsResponse]:
        """
        Get problems that user attempted but never solved, grouped by tags.

        Returns analysis of failed attempts across different topics. This helps identify
        weak areas where the user frequently struggles.

        Args:
            handle: Codeforces handle
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Abandoned problems analysis grouped by tags
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
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

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
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

            # Enqueue background refresh (non-blocking)
            asyncio.create_task(task_queue.enqueue(handle))

            return Response(
                response,
                headers={
                    **self._cache_headers(0),
                    "X-Data-Stale": "true",
                    "X-Data-Age": str(age),
                },
            )

        # Case 3: No data or prefer_fresh
        try:
            task_id = await task_queue.enqueue(handle)
            return Response(
                content={"status": "processing", "task_id": task_id, "retry_after": 2},
                status_code=202,
            )
        except Exception:
            # Fallback: try fetching directly if queue fails
            try:
                submissions = await data_service.get_user_submissions(handle)
            except UserNotFoundError:
                raise HTTPException(
                    status_code=404, detail=f"User '{handle}' not found on Codeforces"
                )

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

            return Response(response, headers=self._cache_headers(14400))

    @get(
        path="/by-ratings/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "abandoned_service": abandoned_problems_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_abandoned_problems_by_ratings(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        abandoned_service: AbandonedProblemsService,
        redis: Redis,
        task_queue: TaskQueue,
        prefer_fresh: bool = Parameter(
            default=False,
            description="If true, force refresh even if stale data is available",
        ),
    ) -> Response[AbandonedProblemByRatingsResponse]:
        """
        Get problems that user attempted but never solved, grouped by rating bins.

        Shows the difficulty levels where user faces the most challenges and frequently
        abandons problems without solving them.

        Args:
            handle: Codeforces handle
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Abandoned problems analysis grouped by rating bins
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
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

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
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

            # Enqueue background refresh (non-blocking)
            asyncio.create_task(task_queue.enqueue(handle))

            return Response(
                response,
                headers={
                    **self._cache_headers(0),
                    "X-Data-Stale": "true",
                    "X-Data-Age": str(age),
                },
            )

        # Case 3: No data or prefer_fresh
        try:
            task_id = await task_queue.enqueue(handle)
            return Response(
                content={"status": "processing", "task_id": task_id, "retry_after": 2},
                status_code=202,
            )
        except Exception:
            # Fallback: try fetching directly if queue fails
            try:
                submissions = await data_service.get_user_submissions(handle)
            except UserNotFoundError:
                raise HTTPException(
                    status_code=404, detail=f"User '{handle}' not found on Codeforces"
                )

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

            return Response(response, headers=self._cache_headers(14400))
