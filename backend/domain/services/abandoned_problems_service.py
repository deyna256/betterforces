"""Abandoned problems analysis service."""

from collections import defaultdict
from typing import Dict, List

from backend.domain.models.abandoned_problems import (
    AbandonedProblem,
    AbandonedProblemsAnalysis,
    RatingAbandonedStats,
    TagAbandonedStats,
)
from backend.domain.models.codeforces import Submission
from backend.domain.services.base import BaseMetricService


class AbandonedProblemsService(BaseMetricService):
    """Service for analyzing abandoned problems (attempted but never solved)."""

    @staticmethod
    def analyze_abandoned_problems(
        handle: str, submissions: List[Submission]
    ) -> AbandonedProblemsAnalysis:
        """
        Analyze user's submissions to find problems that were attempted but never solved.

        Args:
            handle: Codeforces handle
            submissions: List of user's submissions

        Returns:
            Analysis of abandoned problems with aggregations by tags and ratings
        """
        if not submissions:
            return AbandonedProblemsAnalysis(
                handle=handle,
                abandoned_problems=[],
                total_abandoned=0,
                tags_stats=[],
                ratings_stats=[],
            )

        # Group submissions by problem to find abandoned ones
        attempted_problems = AbandonedProblemsService._group_submissions_by_problem(submissions)
        abandoned_problems = AbandonedProblemsService._find_abandoned_problems(attempted_problems)

        # Aggregate statistics by tags and ratings
        tags_stats = AbandonedProblemsService._aggregate_by_tags(abandoned_problems)
        ratings_stats = AbandonedProblemsService._aggregate_by_ratings(abandoned_problems)

        return AbandonedProblemsAnalysis(
            handle=handle,
            abandoned_problems=abandoned_problems,
            total_abandoned=len(abandoned_problems),
            tags_stats=sorted(tags_stats, key=lambda x: x.problem_count, reverse=True),
            ratings_stats=sorted(ratings_stats, key=lambda x: x.problem_count, reverse=True),
        )

    @staticmethod
    def _group_submissions_by_problem(submissions: List[Submission]) -> Dict[str, List[Submission]]:
        """Group submissions by unique problem key."""
        grouped = defaultdict(list)
        for submission in submissions:
            problem_key = submission.problem.problem_key
            grouped[problem_key].append(submission)
        return dict(grouped)

    @staticmethod
    def _find_abandoned_problems(
        attempted_problems: Dict[str, List[Submission]],
    ) -> List[AbandonedProblem]:
        """Find problems that were attempted but never solved."""
        abandoned_problems = []

        for problem_key, problem_submissions in attempted_problems.items():
            # Check if any submission was accepted
            has_solved = any(sub.is_solved for sub in problem_submissions)

            if has_solved:
                continue

            # If not solved, create abandoned problem record
            problem = problem_submissions[0].problem  # All submissions have same problem data
            failed_attempts = len(problem_submissions)

            abandoned_problem = AbandonedProblem(
                contest_id=problem.contest_id,
                index=problem.index,
                name=problem.name,
                rating=problem.rating or 0,
                tags=problem.tags,
                failed_attempts=failed_attempts,
            )
            abandoned_problems.append(abandoned_problem)

        return abandoned_problems

    @staticmethod
    def _aggregate_by_tags(abandoned_problems: List[AbandonedProblem]) -> List[TagAbandonedStats]:
        """Aggregate abandoned problems statistics by tags."""
        tag_stats = defaultdict(lambda: {"problems": set(), "attempts": 0})

        for problem in abandoned_problems:
            for tag in problem.tags:
                tag_stats[tag]["problems"].add(problem.name)
                tag_stats[tag]["attempts"] += problem.failed_attempts

        # Convert to TagAbandonedStats objects
        tags_stats = []
        for tag, stats in tag_stats.items():
            tag_stat = TagAbandonedStats(
                tag=tag,
                problem_count=len(stats["problems"]),
                total_failed_attempts=stats["attempts"],
            )
            tags_stats.append(tag_stat)

        return tags_stats

    @staticmethod
    def _aggregate_by_ratings(
        abandoned_problems: List[AbandonedProblem],
    ) -> List[RatingAbandonedStats]:
        """Aggregate abandoned problems statistics by ratings."""
        rating_stats = defaultdict(lambda: {"problems": 0, "attempts": 0})

        for problem in abandoned_problems:
            if problem.rating > 0:  # Skip problems without ratings
                rating_bin = (
                    problem.rating // 100
                ) * 100  # Group by 100-point bins (800, 900, 1000...)
                rating_stats[rating_bin]["problems"] += 1
                rating_stats[rating_bin]["attempts"] += problem.failed_attempts

        # Convert to RatingAbandonedStats objects
        ratings_stats = []
        for rating, stats in rating_stats.items():
            rating_stat = RatingAbandonedStats(
                rating=rating,
                problem_count=stats["problems"],
                total_failed_attempts=stats["attempts"],
            )
            ratings_stats.append(rating_stat)

        return ratings_stats
