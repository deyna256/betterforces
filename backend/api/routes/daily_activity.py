"""Daily activity API routes."""

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
    daily_activity_service_dependency,
    redis_dependency,
    task_queue_dependency,
)
from backend.api.routes.base import BaseMetricController
from backend.domain.models.time_period import TimePeriod
from backend.api.schemas.daily_activity import (
    DailyActivityItemSchema,
    DailyActivityResponse,
)
from backend.api.schemas.common import AsyncTaskResponse
from backend.domain.services.daily_activity_service import DailyActivityService
from backend.services.codeforces_data_service import CodeforcesDataService
from backend.infrastructure.codeforces_client import UserNotFoundError
from backend.infrastructure.task_queue import TaskQueue


class DailyActivityController(BaseMetricController):
    """Controller for daily activity endpoints."""

    path = "/daily-activity"
    tags = ["Daily Activity"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "daily_activity_service": daily_activity_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_daily_activity(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        daily_activity_service: DailyActivityService,
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
    ) -> Union[Response[DailyActivityResponse], Response[AsyncTaskResponse]]:
        """
        Get user's daily submission activity.

        Returns per-day counts of solved problems and failed attempts,
        with zero-filled gaps for days without activity.
        """
        now = datetime.now(timezone.utc)
        start_date = period.to_start_date(now=now)
        end_date_val = now.date()
        start_date_val = start_date.date() if start_date else None

        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
            submissions = self._filter_by_date_range(submissions, start_date=start_date)
            analysis = daily_activity_service.analyze(
                handle, submissions, start_date=start_date_val, end_date=end_date_val
            )
            response = self._build_response(analysis)
            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            submissions = self._filter_by_date_range(submissions, start_date=start_date)
            analysis = daily_activity_service.analyze(
                handle, submissions, start_date=start_date_val, end_date=end_date_val
            )
            response = self._build_response(analysis)

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
            try:
                submissions = await data_service.get_user_submissions(handle)
            except UserNotFoundError:
                raise HTTPException(
                    status_code=404, detail=f"User '{handle}' not found on Codeforces"
                )

            submissions = self._filter_by_date_range(submissions, start_date=start_date)
            self._validate_submissions_exist(submissions, handle)

            analysis = daily_activity_service.analyze(
                handle, submissions, start_date=start_date_val, end_date=end_date_val
            )
            response = self._build_response(analysis)
            return Response(response, headers=self._cache_headers(14400))

    def _build_response(self, analysis) -> DailyActivityResponse:
        """Build response schema from analysis result."""
        days = [
            DailyActivityItemSchema(
                date=day.date,
                solved_count=day.solved_count,
                attempt_count=day.attempt_count,
            )
            for day in analysis.days
        ]
        return DailyActivityResponse(
            days=days,
            total_solved=analysis.total_solved,
            total_attempts=analysis.total_attempts,
            active_days=analysis.active_days,
            last_updated=self.get_current_timestamp(),
        )
