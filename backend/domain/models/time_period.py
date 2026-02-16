"""Time period enum for filtering submissions by date range."""

from datetime import datetime, timedelta
from enum import Enum


class TimePeriod(str, Enum):
    """Configurable time periods for filtering submissions."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    HALF_YEAR = "half_year"
    YEAR = "year"
    ALL_TIME = "all_time"

    def to_start_date(self, now: datetime) -> datetime | None:
        """Convert time period to a start date relative to the given timestamp.

        Args:
            now: The reference timestamp (should be timezone-aware UTC)

        Returns:
            Start datetime for the period, or None for ALL_TIME
        """
        if self is TimePeriod.ALL_TIME:
            return None

        if self is TimePeriod.HOUR:
            return now - timedelta(hours=1)

        if self is TimePeriod.DAY:
            return now - timedelta(days=1)

        if self is TimePeriod.WEEK:
            return now - timedelta(weeks=1)

        if self is TimePeriod.MONTH:
            # Go back one month, handling edge cases
            month = now.month - 1
            year = now.year
            if month == 0:
                month = 12
                year -= 1
            day = min(now.day, _days_in_month(year, month))
            return now.replace(year=year, month=month, day=day)

        if self is TimePeriod.HALF_YEAR:
            # Go back 6 months
            month = now.month - 6
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            day = min(now.day, _days_in_month(year, month))
            return now.replace(year=year, month=month, day=day)

        # YEAR
        year = now.year - 1
        day = min(now.day, _days_in_month(year, now.month))
        return now.replace(year=year, day=day)


def _days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month/year."""
    if month == 12:
        return 31
    return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
