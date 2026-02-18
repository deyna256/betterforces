"""Difficulty distribution service for analyzing problem difficulty distribution."""

from collections import defaultdict
from typing import List

from backend.domain.models.codeforces import Submission
from backend.domain.models.difficulty_distribution import (
    DifficultyDistribution,
    RatingRange,
)
from backend.domain.services.base import SubmissionProcessor


class DifficultyDistributionService():
    """Service for generating difficulty distribution analytics."""

    # Standard rating bins for Codeforces (100-point intervals)
    RATING_BINS = [
        800,
        900,
        1000,
        1100,
        1200,
        1300,
        1400,
        1500,
        1600,
        1700,
        1800,
        1900,
        2000,
        2100,
        2200,
        2300,
        2400,
        2500,
        2600,
        2700,
        2800,
        2900,
        3000,
        3100,
        3200,
        3300,
        3400,
        3500,
    ]

    @staticmethod
    def analyze_difficulty_distribution(
        handle: str, submissions: List[Submission]
    ) -> DifficultyDistribution:
        """
        Analyze user's solved problems and create difficulty distribution by rating bins.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions

        Returns:
            DifficultyDistribution with analyzed data
        """
        # Filter successful submissions
        processor = SubmissionProcessor(submissions)
        successful_submissions = processor._filter_successful_submissions()

        if not successful_submissions:
            return DifficultyDistribution(
                handle=handle,
                ranges=[],
                total_solved=0,
            )

        # Remove duplicate problems (keep first solve)
        unique_solves = processor._deduplicate_problems()

        # Group problems by rating bins
        bin_counts = DifficultyDistributionService._create_bin_distribution(unique_solves)

        # Create RatingRange objects
        ranges = []
        for rating_bin, count in sorted(bin_counts.items()):
            range_obj = RatingRange(
                rating=rating_bin,
                problem_count=count,
            )
            ranges.append(range_obj)

        return DifficultyDistribution(
            handle=handle,
            ranges=ranges,
            total_solved=len(unique_solves),
        )

    @staticmethod
    def _create_bin_distribution(submissions: List[Submission]) -> dict[int, int]:
        """Create distribution of problems across rating bins."""
        bin_counts = defaultdict(int)

        for submission in submissions:
            if submission.problem.rating is None:
                continue

            # Find the appropriate bin for this rating
            bin_rating = DifficultyDistributionService._get_rating_bin(submission.problem.rating)
            bin_counts[bin_rating] += 1

        return dict(bin_counts)

    @staticmethod
    def _get_rating_bin(rating: int) -> int:
        """Get the rating bin for a given rating (floor to nearest 100)."""
        return (rating // 100) * 100
