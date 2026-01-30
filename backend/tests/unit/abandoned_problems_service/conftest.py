"""Shared test fixtures for the Abandoned Problems Service unit tests."""

import datetime
import pytest

from typing import Callable, List
from unittest.mock import Mock

from backend.domain.models.codeforces import Problem, Submission, SubmissionStatus


@pytest.fixture
def mock_submission() -> Callable[..., Mock]:
    """
    Fixture that returns a factory function to create mock submissions.
    Usage in tests: mock_submission(contest_id=1, index='A', ...)
    """

    def _create(
        contest_id: int,
        index: str,
        name: str,
        rating: int | None,
        tags: List[str],
        verdict: SubmissionStatus = SubmissionStatus.OK,
        programming_language: str = "Python 3",
        is_solved: bool = False,
    ) -> Mock:
        mock_problem = Mock(spec=Problem)
        mock_problem.contest_id = contest_id
        mock_problem.index = index
        mock_problem.name = name
        mock_problem.rating = rating
        mock_problem.tags = tags
        mock_problem.problem_key = f"{contest_id}{index}"

        mock_submission = Mock(spec=Submission)
        mock_submission.contest_id = contest_id
        mock_submission.creation_time_seconds = datetime.datetime.now().second
        mock_submission.problem = mock_problem
        mock_submission.verdict = verdict
        mock_submission.programming_language = programming_language
        mock_submission.is_solved = is_solved

        return mock_submission

    return _create
