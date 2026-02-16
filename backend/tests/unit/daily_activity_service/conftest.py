from typing import Callable, List
from unittest.mock import Mock

import pytest

from backend.domain.models.codeforces import Problem, Submission, SubmissionStatus


@pytest.fixture
def mock_submission() -> Callable[..., Mock]:

    def _create(
        contest_id: int,
        index: str,
        name: str,
        creation_time_seconds: int,
        rating: int | None = None,
        tags: List[str] | None = None,
        verdict: SubmissionStatus = SubmissionStatus.OK,
        programming_language: str = "Python 3",
        is_solved: bool = True,
    ) -> Mock:
        mock_problem = Mock(spec=Problem)
        mock_problem.contest_id = contest_id
        mock_problem.index = index
        mock_problem.name = name
        mock_problem.rating = rating
        mock_problem.tags = tags or []
        mock_problem.problem_key = f"{contest_id}{index}"

        mock_sub = Mock(spec=Submission)
        mock_sub.contest_id = contest_id
        mock_sub.creation_time_seconds = creation_time_seconds
        mock_sub.problem = mock_problem
        mock_sub.verdict = verdict
        mock_sub.programming_language = programming_language
        mock_sub.is_solved = is_solved

        return mock_sub

    return _create
