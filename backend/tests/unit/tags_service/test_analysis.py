from backend.domain.models.codeforces import SubmissionStatus
from backend.domain.services.tags_service import TagsService


def test_returns_zero_counts_and_ratings_when_no_submissions() -> None:
    analysis = TagsService.analyze_tags("test_user", [])

    assert analysis.handle == "test_user"
    assert analysis.total_solved == 0
    assert analysis.tags == []
    assert analysis.overall_average_rating == 0
    assert analysis.overall_median_rating == 0


def test_no_successful_submissions_and_returns_zero_stats(mock_submission) -> None:
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
            tags=["implementation"],
            verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            is_solved=False,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.handle == "test_user"
    assert analysis.total_solved == 0
    assert analysis.tags == []
    assert analysis.overall_average_rating == 0
    assert analysis.overall_median_rating == 0


def test_returns_zero_rating_stats_when_all_ratings_are_missing(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=None, tags=["math"], is_solved=True
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=None,
            tags=["implementation"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.handle == "test_user"
    assert analysis.total_solved == 2
    assert analysis.tags == []
    assert analysis.overall_average_rating == 0
    assert analysis.overall_median_rating == 0


def test_does_not_create_tag_stats_when_solved_problems_have_no_tags(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=800, tags=[], is_solved=True
        ),
        mock_submission(
            contest_id=100, index="B", name="Problem B", rating=1200, tags=[], is_solved=True
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.handle == "test_user"
    assert analysis.total_solved == 2
    assert analysis.tags == []
    assert analysis.overall_average_rating == 1000.0
    assert analysis.overall_median_rating == 1000.0


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

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 1
    assert len(analysis.tags) == 1
    assert analysis.tags[0].tag == "math"
    assert analysis.tags[0].problem_count == 1


def test_counts_only_unique_problems_across_multiple_submissions(mock_submission) -> None:
    submissions = [
        # Problem A solved 3 times
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=800, tags=["math"], is_solved=True
        ),
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=800, tags=["math"], is_solved=True
        ),
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=800, tags=["math"], is_solved=True
        ),
        # Problem B solved once
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1200,
            tags=["dp"],
            is_solved=True,
        ),
        # Problem C solved twice
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["greedy"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 3
    assert len(analysis.tags) == 3


def test_creates_single_tag_stat_for_one_solved_problem(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1200,
            tags=["math"],
            is_solved=True,
        )
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 1
    assert len(analysis.tags) == 1

    tag_info = analysis.tags[0]
    assert tag_info.tag == "math"
    assert tag_info.average_rating == 1200.0
    assert tag_info.median_rating == 1200.0
    assert tag_info.problem_count == 1
    assert tag_info.problems == ["Problem A"]

    assert analysis.overall_average_rating == 1200.0
    assert analysis.overall_median_rating == 1200.0


def test_aggregates_ratings_and_counts_for_multiple_problems_with_same_tag(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1000,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["implementation"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 3
    assert len(analysis.tags) == 1

    tag_info = analysis.tags[0]
    assert tag_info.tag == "implementation"
    assert tag_info.average_rating == 1000.0
    assert tag_info.median_rating == 1000.0
    assert tag_info.problem_count == 3

    assert analysis.overall_average_rating == 1000.0
    assert analysis.overall_median_rating == 1000.0


def test_creates_stats_for_each_tag_when_problem_has_multiple_tags(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1400,
            tags=["dp", "greedy"],
            is_solved=True,
        )
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 1
    assert len(analysis.tags) == 2

    # Both tags should have the same statistics
    for tag_info in analysis.tags:
        assert tag_info.tag in ["dp", "greedy"]
        assert tag_info.average_rating == 1400.0
        assert tag_info.median_rating == 1400.0
        assert tag_info.problem_count == 1


def test_creates_separate_stats_for_each_tag_across_problems(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100, index="A", name="Problem A", rating=800, tags=["math"], is_solved=True
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1200,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["greedy"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 3
    assert len(analysis.tags) == 3

    # Check each tag has count of 1
    for tag_info in analysis.tags:
        assert tag_info.problem_count == 1


def test_aggregates_shared_tags_across_multiple_problems(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=1200,
            tags=["math", "dp"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1400,
            tags=["math", "greedy"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["dp"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert analysis.total_solved == 3
    assert len(analysis.tags) == 3

    # Find each tag and check statistics
    math_tag = next(t for t in analysis.tags if t.tag == "math")
    assert math_tag.average_rating == 1300.0  # (1200 + 1400) / 2
    assert math_tag.median_rating == 1300.0
    assert math_tag.problem_count == 2
    assert sorted(math_tag.problems) == ["Problem A", "Problem B"]

    dp_tag = next(t for t in analysis.tags if t.tag == "dp")
    assert dp_tag.average_rating == 1100.0  # (1200 + 1000) / 2
    assert dp_tag.median_rating == 1100.0
    assert dp_tag.problem_count == 2
    assert sorted(dp_tag.problems) == ["Problem A", "Problem C"]

    greedy_tag = next(t for t in analysis.tags if t.tag == "greedy")
    assert greedy_tag.average_rating == 1400.0
    assert greedy_tag.median_rating == 1400.0
    assert greedy_tag.problem_count == 1
    assert greedy_tag.problems == ["Problem B"]


def test_computes_average_and_median_for_even_number_of_problems(mock_submission) -> None:
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
            rating=1000,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1200,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="D",
            name="Problem D",
            rating=1400,
            tags=["math"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    tag_info = analysis.tags[0]
    assert tag_info.average_rating == 1100.0  # (800 + 1000 + 1200 + 1400) / 4
    assert tag_info.median_rating == 1100.0  # (1000 + 1200) / 2


def test_computes_median_for_odd_number_of_problems(mock_submission) -> None:
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
            rating=1200,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1600,
            tags=["math"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    tag_info = analysis.tags[0]
    assert tag_info.average_rating == 1200.0  # (800 + 1200 + 1600) / 3
    assert tag_info.median_rating == 1200.0  # Middle value


def test_rounds_average_rating_to_expected_precision(mock_submission) -> None:
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
            rating=900,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["math"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    tag_info = analysis.tags[0]
    assert tag_info.average_rating == 900.0  # (800 + 900 + 1000) / 3 = 900.0
    assert tag_info.median_rating == 900.0


def test_sorts_tags_by_problem_count_descending(mock_submission) -> None:
    submissions = [
        # 5 problems with "implementation"
        mock_submission(
            contest_id=100,
            index="A",
            name="Problem A",
            rating=800,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=900,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1000,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="D",
            name="Problem D",
            rating=1100,
            tags=["implementation"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=100,
            index="E",
            name="Problem E",
            rating=1200,
            tags=["implementation"],
            is_solved=True,
        ),
        # 3 problems with "math"
        mock_submission(
            contest_id=200,
            index="A",
            name="Problem F",
            rating=800,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="B",
            name="Problem G",
            rating=900,
            tags=["math"],
            is_solved=True,
        ),
        mock_submission(
            contest_id=200,
            index="C",
            name="Problem H",
            rating=1000,
            tags=["math"],
            is_solved=True,
        ),
        # 1 problem with "dp"
        mock_submission(
            contest_id=300,
            index="A",
            name="Problem I",
            rating=1400,
            tags=["dp"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    assert len(analysis.tags) == 3
    # Check sorting: implementation(5) > math(3) > dp(1)
    assert analysis.tags[0].tag == "implementation"
    assert analysis.tags[0].problem_count == 5
    assert analysis.tags[1].tag == "math"
    assert analysis.tags[1].problem_count == 3
    assert analysis.tags[2].tag == "dp"
    assert analysis.tags[2].problem_count == 1


def test_sorts_problem_names_alphabetically_within_each_tag(mock_submission) -> None:
    submissions = [
        mock_submission(
            contest_id=100,
            index="C",
            name="Problem C",
            rating=1200,
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
        mock_submission(
            contest_id=100,
            index="B",
            name="Problem B",
            rating=1000,
            tags=["math"],
            is_solved=True,
        ),
    ]

    analysis = TagsService.analyze_tags("test_user", submissions)

    tag_info = analysis.tags[0]
    assert tag_info.problems == ["Problem A", "Problem B", "Problem C"]
