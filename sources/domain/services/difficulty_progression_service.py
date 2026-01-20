"""Difficulty progression service for analyzing problem difficulty growth over time."""

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean
from typing import Dict, List

from sources.domain.models.codeforces import Submission
from sources.domain.models.difficulty_progression import (
    DifficultyPoint,
    DifficultyProgression,
    GrowthRate,
)
from sources.domain.services.base import BaseMetricService


class DifficultyProgressionService(BaseMetricService):
    """Service for generating difficulty progression analytics."""

    @staticmethod
    def analyze_difficulty_progression(
        handle: str, submissions: List[Submission]
    ) -> DifficultyProgression:
        """
        Analyze user's problem-solving difficulty progression over time.

        Groups solved problems by monthly/quarterly periods and calculates
        average ratings and growth rates.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions

        Returns:
            DifficultyProgression with analyzed data
        """
        # Filter successful submissions
        successful_submissions = [s for s in submissions if s.is_solved]

        if not successful_submissions:
            now = datetime.now(timezone.utc)
            return DifficultyProgression(
                handle=handle,
                monthly_progression=[],
                quarterly_progression=[],
                growth_rates=[],
                total_solved=0,
                periods_analyzed=0,
                first_solve_date=now,
                latest_solve_date=now,
            )

        # Remove duplicate problems (keep first solve)
        unique_solves = DifficultyProgressionService._deduplicate_problems(successful_submissions)

        # Group by periods
        monthly_data = DifficultyProgressionService._group_by_month(unique_solves)
        quarterly_data = DifficultyProgressionService._group_by_quarter(unique_solves)

        # Convert to DifficultyPoint objects
        monthly_progression = DifficultyProgressionService._create_difficulty_points(
            monthly_data, "month"
        )
        quarterly_progression = DifficultyProgressionService._create_difficulty_points(
            quarterly_data, "quarter"
        )

        # Calculate growth rates
        monthly_growth_rates = DifficultyProgressionService._calculate_growth_rates(
            monthly_progression, "month"
        )
        quarterly_growth_rates = DifficultyProgressionService._calculate_growth_rates(
            quarterly_progression, "quarter"
        )

        # Get date ranges
        first_solve_date = min(s.creation_time_seconds for s in unique_solves)
        latest_solve_date = max(s.creation_time_seconds for s in unique_solves)

        return DifficultyProgression(
            handle=handle,
            monthly_progression=monthly_progression,
            quarterly_progression=quarterly_progression,
            growth_rates=monthly_growth_rates + quarterly_growth_rates,
            total_solved=len(unique_solves),
            periods_analyzed=len(monthly_progression) + len(quarterly_progression),
            first_solve_date=datetime.fromtimestamp(first_solve_date, tz=timezone.utc),
            latest_solve_date=datetime.fromtimestamp(latest_solve_date, tz=timezone.utc),
        )

    @staticmethod
    def _group_by_month(submissions: List[Submission]) -> Dict[str, List[Submission]]:
        """Group submissions by year-month."""
        groups: Dict[str, List[Submission]] = defaultdict(list)

        for submission in submissions:
            dt = datetime.fromtimestamp(submission.creation_time_seconds, tz=timezone.utc)
            key = f"{dt.year:04d}-{dt.month:02d}"
            groups[key].append(submission)

        return dict(groups)

    @staticmethod
    def _group_by_quarter(submissions: List[Submission]) -> Dict[str, List[Submission]]:
        """Group submissions by year-quarter."""
        groups: Dict[str, List[Submission]] = defaultdict(list)

        for submission in submissions:
            dt = datetime.fromtimestamp(submission.creation_time_seconds, tz=timezone.utc)
            quarter = ((dt.month - 1) // 3) + 1
            key = f"{dt.year:04d}-Q{quarter}"
            groups[key].append(submission)

        return dict(groups)

    @staticmethod
    def _create_difficulty_points(
        grouped_data: Dict[str, List[Submission]], period_type: str
    ) -> List[DifficultyPoint]:
        """Convert grouped data to DifficultyPoint objects."""
        points = []

        for period_key, period_submissions in grouped_data.items():
            # Filter submissions with ratings and calculate average
            rated_submissions = [s for s in period_submissions if s.problem.rating is not None]

            if rated_submissions:
                ratings = [s.problem.rating for s in rated_submissions]
                avg_rating = mean(ratings)

                if period_type == "month":
                    # Parse YYYY-MM format
                    year, month = map(int, period_key.split("-"))
                    period_start_dt = datetime(year, month, 1, tzinfo=timezone.utc)
                    if month == 12:
                        period_end_dt = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
                    else:
                        period_end_dt = datetime(year, month + 1, 1, tzinfo=timezone.utc)
                    date_month = period_key
                    date_quarter = f"{year:04d}-Q{((month - 1) // 3) + 1}"
                else:  # quarter
                    # Parse YYYY-QN format
                    year_str, quarter_str = period_key.split("-")
                    year = int(year_str)
                    quarter = int(quarter_str[1])  # Remove 'Q'

                    month_start = (quarter - 1) * 3 + 1
                    period_start_dt = datetime(year, month_start, 1, tzinfo=timezone.utc)

                    if quarter == 4:
                        period_end_dt = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
                    else:
                        period_end_dt = datetime(year, month_start + 3, 1, tzinfo=timezone.utc)
                    date_month = f"{year:04d}-{month_start:02d}"
                    date_quarter = period_key

                point = DifficultyPoint(
                    date_month=date_month,
                    date_quarter=date_quarter,
                    average_rating=round(avg_rating, 1),
                    problem_count=len(rated_submissions),
                    period_start=period_start_dt,
                    period_end=period_end_dt,
                )

                points.append(point)

        # Sort by period start date
        points.sort(key=lambda x: x.period_start)
        return points

    @staticmethod
    def _calculate_growth_rates(
        difficulty_points: List[DifficultyPoint], period_type: str
    ) -> List[GrowthRate]:
        """Calculate growth rates between consecutive periods."""
        if len(difficulty_points) < 2:
            return []

        growth_rates = []

        for i in range(1, len(difficulty_points)):
            current = difficulty_points[i]
            previous = difficulty_points[i - 1]

            rating_change = current.average_rating - previous.average_rating

            # Calculate number of months between periods
            if period_type == "month":
                months_diff = 1
            else:  # quarter
                months_diff = 3

            monthly_growth = rating_change / months_diff if months_diff > 0 else 0

            growth_rate = GrowthRate(
                from_period=previous.date_month
                if period_type == "month"
                else previous.date_quarter,
                to_period=current.date_month if period_type == "month" else current.date_quarter,
                rating_change=round(rating_change, 1),
                monthly_growth=round(monthly_growth, 1),
                months_difference=months_diff,
            )

            growth_rates.append(growth_rate)

        return growth_rates
