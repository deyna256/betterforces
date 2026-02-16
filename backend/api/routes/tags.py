"""Tags API routes."""

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
    tags_service_dependency,
    redis_dependency,
    task_queue_dependency,
)
from backend.api.routes.base import BaseMetricController
from backend.domain.models.time_period import TimePeriod
from backend.api.schemas.tags import SimpleTagInfoSchema, TagsResponse, WeakTagsResponse
from backend.api.schemas.common import AsyncTaskResponse
from backend.domain.services.tags_service import TagsService
from backend.services.codeforces_data_service import CodeforcesDataService
from backend.infrastructure.codeforces_client import UserNotFoundError
from backend.infrastructure.task_queue import TaskQueue


class TagsController(BaseMetricController):
    """Controller for tag ratings endpoints."""

    path = "/tag-ratings"
    tags = ["Tag Ratings"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_tag_ratings(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        tags_service: TagsService,
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
    ) -> Union[Response[TagsResponse], Response[AsyncTaskResponse]]:
        """
        Get user's average and median rating by problem tags.

        Returns performance analysis showing median and average rating for each tag,
        helping identify strengths and weaknesses in different topics.

        Args:
            handle: Codeforces handle
            period: Time period to filter submissions by
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Tag ratings with median and average ratings by tag
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in tags_analysis.tags]

            response = TagsResponse(
                tags=tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in tags_analysis.tags]

            response = TagsResponse(
                tags=tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
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

            tags_analysis = tags_service.analyze_tags(handle, submissions)

            tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in tags_analysis.tags]

            response = TagsResponse(
                tags=tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400))

    @get(
        path="/{handle:str}/weak",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
            "redis": redis_dependency,
            "task_queue": task_queue_dependency,
        },
    )
    async def get_weak_tag_ratings(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        tags_service: TagsService,
        redis: Redis,
        task_queue: TaskQueue,
        threshold: int = Parameter(
            default=200,
            ge=0,
            le=1000,
            description="Minimum rating difference to consider a tag rating 'weak'",
        ),
        period: TimePeriod = Parameter(
            default=TimePeriod.ALL_TIME,
            description="Time period to filter submissions by",
        ),
        prefer_fresh: bool = Parameter(
            default=False,
            description="If true, force refresh even if stale data is available",
        ),
    ) -> Union[Response[WeakTagsResponse], Response[AsyncTaskResponse]]:
        """
        Get user's weak tag ratings - topics where median rating is significantly lower.

        Returns tags that may need more practice based on rating threshold from overall median.

        Args:
            handle: Codeforces handle
            threshold: Minimum rating difference from overall median to be considered weak
            period: Time period to filter submissions by
            prefer_fresh: Force refresh even if stale data exists

        Returns:
            Weak tag ratings analysis
            OR 202 Accepted with task_id if data needs to be fetched
        """
        # Get submissions with staleness check
        submissions, age, is_stale = await self.get_submissions_with_staleness(redis, handle)

        # Case 1: Fresh data (< 4 hours)
        if submissions and not is_stale:
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            weak_tags = tags_analysis.get_weak_tags(threshold)

            weak_tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in weak_tags]

            response = WeakTagsResponse(
                weak_tags=weak_tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
                threshold_used=threshold,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400 - age))

        # Case 2: Stale data (4-24 hours) and !prefer_fresh
        if submissions and is_stale and not prefer_fresh:
            # Return stale data immediately
            submissions = self._filter_by_date_range(
                submissions, start_date=period.to_start_date(now=datetime.now(timezone.utc))
            )
            tags_analysis = tags_service.analyze_tags(handle, submissions)

            weak_tags = tags_analysis.get_weak_tags(threshold)

            weak_tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in weak_tags]

            response = WeakTagsResponse(
                weak_tags=weak_tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
                threshold_used=threshold,
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

            tags_analysis = tags_service.analyze_tags(handle, submissions)

            weak_tags = tags_analysis.get_weak_tags(threshold)

            weak_tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in weak_tags]

            response = WeakTagsResponse(
                weak_tags=weak_tags_info,
                overall_average_rating=tags_analysis.overall_average_rating,
                overall_median_rating=tags_analysis.overall_median_rating,
                total_solved=tags_analysis.total_solved,
                threshold_used=threshold,
                last_updated=self.get_current_timestamp(),
            )

            return Response(response, headers=self._cache_headers(14400))
