from typing import List

from backend.domain.models.codeforces import Submission

class SubmissionProcessor:
    """Deduplicates problems and filters successful submissions."""

    def __init__(self,  submissions: List[Submission]):
        """
        Initialize the instance which contains submissions
        
        Args:
            submissions: List of submissions to perform operations on
        """
        self._submissions = submissions

    def _deduplicate_problems(self) -> List[Submission]:
        """
        Keep only the first successful solve for each unique problem.

        Returns:
            List of submissions with only first solve per problem
        """
        seen_problems = set()
        unique_submissions = []

        for submission in self._submissions:
            problem_key = submission.problem.problem_key
            if problem_key not in seen_problems:
                seen_problems.add(problem_key)
                unique_submissions.append(submission)

        self._submissions = unique_submissions
        return self._submissions

    def _filter_successful_submissions(self) -> List[Submission]:
        """
        Filter submissions to only include solved problems.

        Returns:
            List of only solved submissions
        """
        self._submissions = [s for s in self._submissions if s.is_solved]
        return self._submissions