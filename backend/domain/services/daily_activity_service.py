"""Daily activity service for analyzing submission activity with variable granularity."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from backend.domain.models.codeforces import Submission
from backend.domain.models.daily_activity import DailyActivity, DailyActivityAnalysis
from backend.domain.models.time_period import TimePeriod
from backend.domain.services.base import BaseMetricService

_GRANULARITY_MAP = {
    TimePeriod.HOUR: "minute",
    TimePeriod.DAY: "hour",
    TimePeriod.WEEK: "day",
    TimePeriod.MONTH: "day",
    TimePeriod.HALF_YEAR: "month",
    TimePeriod.YEAR: "month",
    TimePeriod.ALL_TIME: "year",
}

_BUCKET_FORMAT = {
    "minute": "%Y-%m-%d %H:%M",
    "hour": "%Y-%m-%d %H:00",
    "day": "%Y-%m-%d",
    "month": "%Y-%m",
    "year": "%Y",
}


def _truncate(dt: datetime, granularity: str) -> datetime:
    if granularity == "minute":
        return dt.replace(second=0, microsecond=0)
    if granularity == "hour":
        return dt.replace(minute=0, second=0, microsecond=0)
    if granularity == "month":
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if granularity == "year":
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _next_month(dt: datetime) -> datetime:
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1)
    return dt.replace(month=dt.month + 1)


_FIXED_STEPS = {
    "minute": timedelta(minutes=1),
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
}


def _advance(current: datetime, granularity: str) -> datetime:
    if granularity == "year":
        return current.replace(year=current.year + 1)
    if granularity == "month":
        return _next_month(current)
    return current + _FIXED_STEPS[granularity]


class DailyActivityService(BaseMetricService):
    """Service for generating activity analytics with variable granularity."""

    @staticmethod
    def analyze(
        handle: str,
        submissions: List[Submission],
        period: TimePeriod = TimePeriod.ALL_TIME,
        now: Optional[datetime] = None,
    ) -> DailyActivityAnalysis:
        """
        Analyze user's submission activity.

        Granularity is determined by period:
        - HOUR      -> per-minute buckets
        - DAY       -> per-hour buckets
        - WEEK/MONTH -> per-day buckets
        - HALF_YEAR/YEAR -> per-month buckets
        - ALL_TIME  -> per-year buckets
        """
        if now is None:
            now = datetime.now(timezone.utc)

        granularity = _GRANULARITY_MAP[period]
        fmt = _BUCKET_FORMAT[granularity]

        if not submissions:
            return DailyActivityAnalysis(
                handle=handle,
                days=[],
                total_solved=0,
                total_attempts=0,
                active_days=0,
            )

        solved_by_bucket: dict[str, set[str]] = defaultdict(set)
        attempts_by_bucket: dict[str, int] = defaultdict(int)

        for sub in submissions:
            dt = datetime.fromtimestamp(sub.creation_time_seconds, tz=timezone.utc)
            bucket = dt.strftime(fmt)
            if sub.is_solved:
                solved_by_bucket[bucket].add(sub.problem.problem_key)
            else:
                attempts_by_bucket[bucket] += 1

        start_date = period.to_start_date(now=now)
        start_dt = _truncate(start_date, granularity) if start_date else None
        end_dt = _truncate(now, granularity)

        if start_dt is None:
            all_buckets = set(solved_by_bucket.keys()) | set(attempts_by_bucket.keys())
            min_bucket = min(all_buckets)
            start_dt = datetime.strptime(min_bucket, fmt).replace(tzinfo=timezone.utc)

        days: List[DailyActivity] = []
        total_solved = 0
        total_attempts = 0
        active_days = 0
        current = start_dt

        while current <= end_dt:
            label = current.strftime(fmt)
            solved = len(solved_by_bucket.get(label, set()))
            attempts = attempts_by_bucket.get(label, 0)
            days.append(
                DailyActivity(
                    date=label,
                    solved_count=solved,
                    attempt_count=attempts,
                )
            )
            total_solved += solved
            total_attempts += attempts
            if solved > 0 or attempts > 0:
                active_days += 1
            current = _advance(current, granularity)

        return DailyActivityAnalysis(
            handle=handle,
            days=days,
            total_solved=total_solved,
            total_attempts=total_attempts,
            active_days=active_days,
        )
