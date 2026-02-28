"""Division problems service for analyzing average problems per division."""

from collections import defaultdict
from typing import Dict, List

from backend.domain.models.codeforces import Submission
from backend.domain.models.division_problems import (
    DivisionProblemsAnalysis,
    DivisionStats,
)
from backend.domain.services.base import BaseMetricService


class DivisionProblemsService(BaseMetricService):
    """Service for generating division problems analytics."""

    # Standard divisions on Codeforces
    DIVISIONS = ["Div. 1", "Div. 2", "Div. 3", "Div. 4"]

    @staticmethod
    def analyze_division_problems(
        handle: str,
        submissions: List[Submission],
        contest_divisions: Dict[int, str | None],
    ) -> DivisionProblemsAnalysis:
        """
        Analyze user's solved problems and calculate average per division.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions
            contest_divisions: Mapping of contest_id to division string

        Returns:
            DivisionProblemsAnalysis with average problems per division
        """
        # Filter successful submissions
        successful_submissions = DivisionProblemsService._filter_successful_submissions(
            submissions
        )

        if not successful_submissions:
            return DivisionProblemsAnalysis(
                handle=handle,
                divisions=[],
                total_contests=0,
                total_problems_solved=0,
            )

        # Remove duplicate problems (keep first solve)
        unique_solves = DivisionProblemsService._deduplicate_problems(successful_submissions)

        # Group problems by contest and division
        division_data = DivisionProblemsService._analyze_by_division(
            unique_solves, contest_divisions
        )

        # Build division stats
        divisions = []
        total_contests = 0
        total_problems = 0

        for div in DivisionProblemsService.DIVISIONS:
            if div in division_data:
                stats = division_data[div]
                contest_count = len(stats["contests"])
                problems_solved = stats["problem_count"]

                if contest_count > 0:
                    avg_problems = round(problems_solved / contest_count, 2)
                    divisions.append(
                        DivisionStats(
                            division=div,
                            contest_count=contest_count,
                            total_problems_solved=problems_solved,
                            average_problems_per_contest=avg_problems,
                        )
                    )
                    total_contests += contest_count
                    total_problems += problems_solved

        return DivisionProblemsAnalysis(
            handle=handle,
            divisions=divisions,
            total_contests=total_contests,
            total_problems_solved=total_problems,
        )

    @staticmethod
    def _analyze_by_division(
        submissions: List[Submission],
        contest_divisions: Dict[int, str | None],
    ) -> Dict[str, Dict]:
        """
        Group submissions by division and count problems per contest.

        Args:
            submissions: List of successful submissions
            contest_divisions: Mapping of contest_id to division

        Returns:
            Dictionary with division -> {contests: set, problem_count: int}
        """
        division_data: Dict[str, Dict] = defaultdict(
            lambda: {"contests": set(), "problem_count": 0}
        )

        for submission in submissions:
            contest_id = submission.contest_id
            division = contest_divisions.get(contest_id)

            if division is None:
                continue

            division_data[division]["contests"].add(contest_id)
            division_data[division]["problem_count"] += 1

        return dict(division_data)
