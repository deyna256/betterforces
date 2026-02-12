from backend.domain.models.codeforces import SubmissionStatus
from backend.domain.services.difficulty_distribution_service import DifficultyDistributionService


def test_returns_empty_ranges_and_zero_total_when_no_submissions() -> None:
    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", [])

    assert result.handle == "test_user"
    assert result.ranges == []
    assert result.total_solved == 0


def test_returns_empty_ranges_when_all_submissions_failed(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            verdict=SubmissionStatus.WRONG_ANSWER,
            is_solved=False,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1200,
            tags=["dp"],
            verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            is_solved=False,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.ranges == []
    assert result.total_solved == 0


def test_returns_single_range_for_one_solved_problem(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=850,
            tags=["math"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 1
    assert len(result.ranges) == 1
    assert result.ranges[0].rating == 800
    assert result.ranges[0].problem_count == 1


def test_counts_problem_only_once_when_solved_multiple_times(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1200,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1200,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1200,
            tags=["math"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 1
    assert len(result.ranges) == 1
    assert result.ranges[0].problem_count == 1


def test_counts_distinct_problems_in_same_bin(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=850,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=899,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 3
    assert len(result.ranges) == 1
    assert result.ranges[0].rating == 800
    assert result.ranges[0].problem_count == 3


def test_sorts_ranges_by_rating_ascending(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1600,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=800,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert [r.rating for r in result.ranges] == [800, 1200, 1600]


def test_skips_unrated_problems_in_ranges_but_counts_in_total(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=None,
            tags=["dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 3
    assert len(result.ranges) == 2
    ratings = [r.rating for r in result.ranges]
    assert 800 in ratings
    assert 1200 in ratings


def test_returns_empty_ranges_when_all_solved_problems_are_unrated(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=None,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=None,
            tags=["dp"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 2
    assert result.ranges == []


def test_filters_out_failed_and_deduplicates_in_mixed_submissions(mock_submission) -> None:
    submissions = [
        # Solved problem A (will be deduplicated)
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        # Failed problem B
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1200,
            tags=["dp"],
            verdict=SubmissionStatus.WRONG_ANSWER,
            is_solved=False,
        ),
        # Solved problem C
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1600,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    result = DifficultyDistributionService.analyze_difficulty_distribution("test_user", submissions)

    assert result.total_solved == 2
    assert len(result.ranges) == 2
    ratings = [r.rating for r in result.ranges]
    assert 800 in ratings
    assert 1600 in ratings


