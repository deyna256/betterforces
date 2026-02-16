"""Difficulty distribution API routes."""

import asyncio
from datetime import datetime, timezone
from typing import Union

from litestar import get
from litestar.params import Parameter
from litestar.response import Response
from litestar.exceptions import HTTPException
from redis.asyncio import Redis

from backend.api.deps import (
    codeforces_data_service_dependency,
    difficulty_distribution_service_dependency,
    redis_dependency,
    task_queue_dependency,
)
from backend.api.routes.base import BaseMetricController
from backend.domain.models.time_period import TimePeriod
from backend.api.schemas.difficulty_distribution import (
    DifficultyDistributionResponse,
    RatingRangeSchema,
)
from backend.api.schemas.common import AsyncTaskResponse
from backend.domain.services.difficulty_distribution_service import DifficultyDistributionService
from backend.services.codeforces_data_service import CodeforcesDataService
from backend.infrastructure.codeforces_client import UserNotFoundError
from backend.infrastructure.task_queue import TaskQueue


class DifficultyDistributionController(BaseMetricController):
    """Controller for difficulty distribution endpoints."""

    path = "/difficulty-distribution"
    tags = ["Difficulty Distribution"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "difficulty_service": difficulty_distribution_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_difficulty_distribution(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        difficulty_service: DifficultyDistributionService,
        redis: Redis,
        task_queue: TaskQueue,
        period: TimePeriod = Parameter(
            default=TimePeriod.ALL_TIME,
            description="Time period to filter submissions by",
        ),
        prefer_fresh: bool = Parameter(
            default=False,
            description="If true, force refresh even if stale data is available",
        ),
    ) -> Union[Response[DifficultyDistributionResponse], Response[AsyncTaskResponse]]:
        """
        Get user's problem-solving distribution by difficulty levels.

        Returns statistics showing how many problems were solved in each
        rating bin (800, 900, 1000...). This helps identify comfort zones,
        practice gaps, and challenge areas.

        Args:
            handle: Codeforces handle
            period: Time period to filter submissions by
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Difficulty distribution analysis with rating bins and percentages
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
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

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
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
                content=AsyncTaskResponse(
                    status="processing", task_id=task_id, retry_after=2
                ).model_dump(),
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

            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
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

            return Response(response, headers=self._cache_headers(14400))
