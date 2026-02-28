"""Division problems API routes."""

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
    division_problems_service_dependency,
    redis_dependency,
    task_queue_dependency,
)
from backend.api.routes.base import BaseMetricController
from backend.domain.models.time_period import TimePeriod
from backend.api.schemas.division_problems import (
    DivisionProblemsResponse,
    DivisionStatsSchema,
)
from backend.api.schemas.common import AsyncTaskResponse
from backend.domain.services.division_problems_service import DivisionProblemsService
from backend.services.codeforces_data_service import CodeforcesDataService
from backend.infrastructure.codeforces_client import UserNotFoundError
from backend.infrastructure.task_queue import TaskQueue


class DivisionProblemsController(BaseMetricController):
    """Controller for division problems endpoints."""

    path = "/division-problems"
    tags = ["Division Problems"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "division_service": division_problems_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_division_problems(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        division_service: DivisionProblemsService,
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
    ) -> Union[Response[DivisionProblemsResponse], Response[AsyncTaskResponse]]:
        """
        Get user's average problems solved per division.

        Returns statistics showing the average number of problems solved per contest
        for each division (Div. 1, Div. 2, Div. 3, Div. 4). This helps identify
        performance across different difficulty levels of contests.

        Args:
            handle: Codeforces handle
            period: Time period to filter submissions by
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Division problems analysis with averages per division
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get contest divisions mapping
        contest_divisions = await data_service.get_contest_divisions()

        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            analysis = division_service.analyze_division_problems(
                handle, submissions, contest_divisions
            )

            divisions = [
                DivisionStatsSchema.model_validate(div) for div in analysis.divisions
            ]

            response = DivisionProblemsResponse(
                divisions=divisions,
                total_contests=analysis.total_contests,
                total_problems_solved=analysis.total_problems_solved,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            analysis = division_service.analyze_division_problems(
                handle, submissions, contest_divisions
            )

            divisions = [
                DivisionStatsSchema.model_validate(div) for div in analysis.divisions
            ]

            response = DivisionProblemsResponse(
                divisions=divisions,
                total_contests=analysis.total_contests,
                total_problems_solved=analysis.total_problems_solved,
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

            analysis = division_service.analyze_division_problems(
                handle, submissions, contest_divisions
            )

            divisions = [
                DivisionStatsSchema.model_validate(div) for div in analysis.divisions
            ]

            response = DivisionProblemsResponse(
                divisions=divisions,
                total_contests=analysis.total_contests,
                total_problems_solved=analysis.total_problems_solved,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400))
