from datetime import datetime, timezone
from typing import List, Optional

from litestar import Controller
from litestar.exceptions import HTTPException

from sources.domain.models.codeforces import Submission


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
