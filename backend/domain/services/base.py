import copy
from typing import List
from backend.domain.models.codeforces import Submission

class SubmissionCollection:
    """Encapsulates submissions with filtering and deduplication operations."""

    def __init__(self, submissions: List[Submission]):
        """
        Initialize an instance which contains original list of submissions.
        
        Args:
            submissions: List of user's submissions
        """
        self._submissions = submissions
    
    def deduplicate_problems(self, submissions: List[Submission]=[]) -> List[Submission]:
        """
        Keep only the first successful solve for each unique problem.

        Args:
            submissions: List of user's submissions to deduplicate

        Returns:
            List of submissions with only first solve per problem
        """
        seen_problems = set()
        unique_submissions = []

        # Preference given to submissions argument
        submissions_copy = submissions if submissions else copy.copy(self._submissions)

        for submission in submissions_copy:
            problem_key = submission.problem.problem_key
            if problem_key not in seen_problems:
                seen_problems.add(problem_key)
                unique_submissions.append(submission)

        return unique_submissions

    def filter_successful_submissions(self) -> List[Submission]:
        """
        Filter submissions to only include solved problems.

        Returns:
            List of only solved submissions
        """
        submissions_copy = copy.copy(self._submissions)
        successful_submissions = [s for s in submissions_copy if s.is_solved]
        return successful_submissions