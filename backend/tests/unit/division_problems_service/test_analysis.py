from backend.domain.models.codeforces import SubmissionStatus
from backend.domain.services.division_problems_service import DivisionProblemsService


def test_returns_empty_divisions_when_no_submissions(sample_contest_divisions) -> None:
    result = DivisionProblemsService.analyze_division_problems(
        "test_user", [], sample_contest_divisions
    )

    assert result.handle == "test_user"
    assert result.divisions == []
    assert result.total_contests == 0
    assert result.total_problems_solved == 0


def test_returns_empty_divisions_when_all_submissions_failed(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            verdict=SubmissionStatus.WRONG_ANSWER,
            is_solved=False,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert result.divisions == []
    assert result.total_contests == 0
    assert result.total_problems_solved == 0


def test_calculates_average_for_single_division(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        # Contest 200 (Div. 2) - 2 problems
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="B",
            name="Problem B",
            rating=1000,
            tags=["dp"],
            is_solved=True,
        ),
        # Contest 201 (Div. 2) - 3 problems
        mock_submission(
            contest_id=201,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=201,
            index="B",
            name="Problem B",
            rating=1000,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=201,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert len(result.divisions) == 1
    assert result.divisions[0].division == "Div. 2"
    assert result.divisions[0].contest_count == 2
    assert result.divisions[0].total_problems_solved == 5
    assert result.divisions[0].average_problems_per_contest == 2.5


def test_calculates_averages_for_multiple_divisions(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        # Contest 100 (Div. 1) - 1 problem
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=2000,
            tags=["math"],
            is_solved=True,
        ),
        # Contest 200 (Div. 2) - 3 problems
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="B",
            name="Problem B",
            rating=1000,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["greedy"],
            is_solved=True,
        ),
        # Contest 300 (Div. 3) - 4 problems
        mock_submission(
            contest_id=300,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=300,
            index="B",
            name="Problem B",
            rating=900,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=300,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["greedy"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=300,
            index="D",
            name="Problem D",
            rating=1100,
            tags=["strings"],
            is_solved=True,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert len(result.divisions) == 3
    assert result.total_contests == 3
    assert result.total_problems_solved == 8

    # Find each division
    div1 = next(d for d in result.divisions if d.division == "Div. 1")
    div2 = next(d for d in result.divisions if d.division == "Div. 2")
    div3 = next(d for d in result.divisions if d.division == "Div. 3")

    assert div1.average_problems_per_contest == 1.0
    assert div2.average_problems_per_contest == 3.0
    assert div3.average_problems_per_contest == 4.0


def test_counts_problem_only_once_when_solved_multiple_times(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert len(result.divisions) == 1
    assert result.divisions[0].total_problems_solved == 1
    assert result.divisions[0].average_problems_per_contest == 1.0


def test_ignores_contests_without_division(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        # Contest 500 (no division)
        mock_submission(
            contest_id=500,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        # Contest 200 (Div. 2)
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert len(result.divisions) == 1
    assert result.divisions[0].division == "Div. 2"
    assert result.total_problems_solved == 1


def test_ignores_contests_not_in_division_mapping(
    mock_submission, sample_contest_divisions
) -> None:
    submissions = [
        # Contest 999 (not in mapping)
        mock_submission(
            contest_id=999,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
    ]

    result = DivisionProblemsService.analyze_division_problems(
        "test_user", submissions, sample_contest_divisions
    )

    assert result.divisions == []
    assert result.total_contests == 0
    assert result.total_problems_solved == 0
