from typing import List

from sources.domain.models.codeforces import Submission


class BaseMetricService:
    """Base class for all metric services with shared functionality."""

    @staticmethod
    def _deduplicate_problems(submissions: List[Submission]) -> List[Submission]:
        """
        Keep only the first successful solve for each unique problem.

        Args:
            submissions: List of submissions to deduplicate

        Returns:
            List of submissions with only first solve per problem
        """
        seen_problems = set()
        unique_submissions = []

        for submission in submissions:
            problem_key = submission.problem.problem_key
            if problem_key not in seen_problems:
                seen_problems.add(problem_key)
                unique_submissions.append(submission)

        return unique_submissions

    @staticmethod
    def _filter_successful_submissions(submissions: List[Submission]) -> List[Submission]:
        """
        Filter submissions to only include solved problems.

        Args:
            submissions: List of all submissions

        Returns:
            List of only solved submissions
        """
        return [s for s in submissions if s.is_solved]
