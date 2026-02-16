"""Daily activity service for analyzing per-day submission activity."""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from backend.domain.models.codeforces import Submission
from backend.domain.models.daily_activity import DailyActivity, DailyActivityAnalysis
from backend.domain.services.base import BaseMetricService


class DailyActivityService(BaseMetricService):
    """Service for generating daily activity analytics."""

    @staticmethod
    def analyze(
        handle: str,
        submissions: List[Submission],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DailyActivityAnalysis:
        """
        Analyze user's daily submission activity.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions
            start_date: Optional start date for gap filling
            end_date: Optional end date for gap filling

        Returns:
            DailyActivityAnalysis with per-day stats
        """
        if not submissions:
            return DailyActivityAnalysis(
                handle=handle,
                days=[],
                total_solved=0,
                total_attempts=0,
                active_days=0,
            )

        # Group submissions by date
        solved_by_day: dict[date, set[str]] = defaultdict(set)
        attempts_by_day: dict[date, int] = defaultdict(int)

        for sub in submissions:
            day = datetime.fromtimestamp(sub.creation_time_seconds, tz=timezone.utc).date()
            if sub.is_solved:
                solved_by_day[day].add(sub.problem.problem_key)
            else:
                attempts_by_day[day] += 1

        # Determine date range for gap filling
        all_days = set(solved_by_day.keys()) | set(attempts_by_day.keys())
        min_day = start_date if start_date else min(all_days)
        max_day = end_date if end_date else max(all_days)

        # Build day-by-day list with gap filling
        days: List[DailyActivity] = []
        total_solved = 0
        total_attempts = 0
        active_days = 0
        current = min_day

        while current <= max_day:
            solved = len(solved_by_day.get(current, set()))
            attempts = attempts_by_day.get(current, 0)
            days.append(
                DailyActivity(
                    date=current.isoformat(),
                    solved_count=solved,
                    attempt_count=attempts,
                )
            )
            total_solved += solved
            total_attempts += attempts
            if solved > 0 or attempts > 0:
                active_days += 1
            current += timedelta(days=1)

        return DailyActivityAnalysis(
            handle=handle,
            days=days,
            total_solved=total_solved,
            total_attempts=total_attempts,
            active_days=active_days,
        )
