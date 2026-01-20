"""Rating distribution service for analyzing solved problems over time."""

from typing import List

from sources.domain.models.codeforces import Submission
from sources.domain.models.rating_distribution import RatingDistribution, RatingPoint
from sources.domain.services.base import BaseMetricService


class RatingDistributionService(BaseMetricService):
    """Service for generating rating distribution analytics."""

    @staticmethod
    def analyze_rating_distribution(
        handle: str, submissions: List[Submission]
    ) -> RatingDistribution:
        """
        Analyze user's solved problems and create rating distribution over time.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions

        Returns:
            RatingDistribution with analyzed data
        """
        # Filter successful submissions
        successful_submissions = [s for s in submissions if s.is_solved]

        if not successful_submissions:
            return RatingDistribution(
                handle=handle,
                rating_points=[],
                max_rating_achieved=0,
                total_solved=0,
                rating_growth_periods=[],
            )

        # Remove duplicate problems (keep first solve)
        unique_solves = RatingDistributionService._deduplicate_problems(successful_submissions)

        # Create rating points
        rating_points = RatingDistributionService._create_rating_points(unique_solves)

        # Calculate max rating
        max_rating = max((p.rating for p in rating_points), default=0)

        # Identify growth periods
        growth_periods = RatingDistributionService._identify_growth_periods(rating_points)

        return RatingDistribution(
            handle=handle,
            rating_points=rating_points,
            max_rating_achieved=max_rating,
            total_solved=len(rating_points),
            rating_growth_periods=growth_periods,
        )

    @staticmethod
    def _create_rating_points(submissions: List[Submission]) -> List[RatingPoint]:
        """Convert successful submissions to rating points."""
        rating_points = []

        for submission in submissions:
            if submission.problem.rating is not None:
                rating_point = RatingPoint(
                    timestamp=submission.creation_time_seconds,
                    rating=submission.problem.rating,
                    problem_name=submission.problem.name,
                )
                rating_points.append(rating_point)

        # Sort by timestamp
        rating_points.sort(key=lambda x: x.timestamp)
        return rating_points

    @staticmethod
    def _identify_growth_periods(rating_points: List[RatingPoint]) -> List[str]:
        """Identify periods of significant rating growth."""
        if len(rating_points) < 2:
            return []

        growth_periods = []
        sorted_points = sorted(rating_points, key=lambda x: x.timestamp)

        # Define significant growth as increase of 200+ rating points
        significant_growth_threshold = 200

        # Track max rating over time
        current_max = 0
        last_max_update_time = None

        for point in sorted_points:
            if point.rating > current_max:
                # Found a new max rating
                if current_max > 0 and point.rating - current_max >= significant_growth_threshold:
                    # Significant growth period
                    if last_max_update_time:
                        start_date = last_max_update_time.strftime("%Y-%m-%d")
                        end_date = point.date.strftime("%Y-%m-%d")
                        period = f"{start_date} to {end_date}: {current_max} → {point.rating} (+{point.rating - current_max})"
                        growth_periods.append(period)

                last_max_update_time = point.date
                current_max = point.rating

        return growth_periods[:5]  # Limit to top 5 growth periods
