import pytest

from backend.domain.services.abandoned_problems_service import AbandonedProblemsService


def test_empty_submissions() -> None:
    """Test with no submissions returns empty stats."""

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", [])

    assert analysis.handle == "test user"
    assert analysis.total_abandoned == 0
    assert analysis.abandoned_problems == []


@pytest.mark.parametrize(
    "submission_history, expected_abandoned_count",
    [
        # Case 1: Failed only -> should be abandoned
        ([("A", False), ("A", False)], 1),
        # Case 2: Failed then solved -> should NOT be abandoned
        ([("B", False), ("B", True)], 0),
        # Case 3: Solved immediately -> should NOT be abandoned
        ([("C", True)], 0),
    ],
)
def test_identify_abandoned_scenarios(
    mock_submission, submission_history, expected_abandoned_count
) -> None:
    """Test various scenarios for identifying abandoned problems."""

    submissions = []
    for i, is_solved in submission_history:
        submissions.append(
            mock_submission(
                contest_id=100,
                index=i,
                name=f"Problem {i}",
                rating=800,
                tags=[],
                is_solved=is_solved,
            )
        )

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", submissions)

    assert analysis.total_abandoned == expected_abandoned_count


@pytest.mark.parametrize("fail_count", [1, 3, 5, 10])
def test_failed_attempts_count(mock_submission, fail_count) -> None:
    """Test that the number of failed attempts is counted correctly."""

    submissions = [
        mock_submission(
            contest_id=5, index="A", name="Problem A", rating=800, tags=[], is_solved=False
        )
        for _ in range(fail_count)
    ]

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", submissions)

    assert analysis.abandoned_problems[0].failed_attempts == fail_count
