import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from litestar import Controller
from litestar.exceptions import HTTPException
from redis.asyncio import Redis

from backend.domain.models.codeforces import Submission


class BaseMetricController(Controller):
    """Base class for all metric controllers with shared functionality."""

    CACHE_HEADERS = {"Cache-Control": "public, max-age=14400"}

    @staticmethod
    def _filter_by_date_range(
        submissions: List[Submission],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Submission]:
        """
        Filter submissions by date range.

        Args:
            submissions: List of submissions to filter
            start_date: Optional start date (inclusive)
            end_date: Optional end date (inclusive)

        Returns:
            Filtered list of submissions
        """
        filtered = submissions

        if start_date is not None:
            start_timestamp = int(start_date.timestamp())
            filtered = [s for s in filtered if s.creation_time_seconds >= start_timestamp]

        if end_date is not None:
            end_timestamp = int(end_date.timestamp())
            filtered = [s for s in filtered if s.creation_time_seconds <= end_timestamp]

        return filtered

    @staticmethod
    def _validate_submissions_exist(submissions: List[Submission], handle: str) -> None:
        """
        Validate that submissions list is not empty.

        Args:
            submissions: List of submissions to check
            handle: User handle for error message

        Raises:
            HTTPException: If submissions list is empty
        """
        if not submissions:
            raise HTTPException(
                status_code=404,
                detail=f"No submissions found for user '{handle}' in the specified date range",
            )

    @staticmethod
    def get_current_timestamp() -> datetime:
        """
        Get current UTC timestamp.

        Returns:
            Current datetime in UTC timezone
        """
        return datetime.now(timezone.utc)

    @staticmethod
    async def get_submissions_with_staleness(
        redis: Redis, handle: str
    ) -> Tuple[Optional[List[Submission]], int, bool]:
        """
        Get submissions from cache with staleness information.

        Args:
            redis: Redis client instance
            handle: Codeforces user handle

        Returns:
            Tuple of (submissions, age_seconds, is_stale)
            - submissions: List of Submission objects or None if not cached
            - age_seconds: Age of cache in seconds
            - is_stale: True if age > 4 hours (14400 seconds)
        """
        from backend.domain.models.codeforces import Problem

        cached = await redis.get(f"submissions:{handle}")
        if not cached:
            return None, 0, False

        ttl = await redis.ttl(f"submissions:{handle}")
        if ttl < 0:  # Key exists but has no TTL or expired
            return None, 0, False

        age = 86400 - ttl  # 24h - remaining TTL = age
        is_stale = age > 14400  # 4 hours

        # Deserialize submissions
        submissions_data = json.loads(cached)
        submissions = []
        for s in submissions_data:
            # Convert nested problem dict to Problem object
            problem_data = s.pop("problem")
            problem = Problem(**problem_data)
            submission = Submission(problem=problem, **s)
            submissions.append(submission)

        return submissions, age, is_stale

    @staticmethod
    def _cache_headers(max_age: int = 14400) -> dict:
        """
        Generate cache headers.

        Args:
            max_age: Cache max age in seconds

        Returns:
            Dictionary with Cache-Control header
        """
        return {"Cache-Control": f"public, max-age={max_age}"}
