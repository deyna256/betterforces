import pytest

from backend.domain.services.abandoned_problems_service import AbandonedProblemsService


@pytest.mark.parametrize(
    "problems_tags, expected_counts",
    [
        # Case 1: Overlapping tags (DP appears twice)
        ([["dp", "greedy"], ["dp", "math"]], {"dp": 2, "greedy": 1, "math": 1}),
        # Case 2: Disjoint tags (No overlap)
        ([["graphs"], ["strings"]], {"graphs": 1, "strings": 1}),
        # Case 3: Same tag repeated across 3 problems
        ([["math"], ["math"], ["math"]], {"math": 3}),
    ],
)
def test_aggregation_by_tags(mock_submission, problems_tags, expected_counts) -> None:
    """Test if abandoned problem are correctly grouped by tags."""

    submissions = []

    for i, tags in enumerate(problems_tags):
        submissions.append(
            mock_submission(
                contest_id=1,
                index=str(i),
                name=f"Problem {i}",
                rating=800,
                tags=tags,
                is_solved=False,
            )
        )

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", submissions)

    for tag, count in expected_counts.items():
        stat = next(s for s in analysis.tags_stats if s.tag == tag)

        assert stat.problem_count == count


@pytest.mark.parametrize(
    "ratings, expected_bins",
    [
        # Case 1: Standard binning (1290 rounds down to 1200)
        ([1200, 1290, 850], {1200: 2, 800: 1}),
        # Case 2: Boundary check (1999 -> 1900, 2000 -> 2000)
        ([1999, 2000, 2001], {1900: 1, 2000: 2}),
        # Case 3: All in same bin
        ([1400, 1450, 1499], {1400: 3}),
    ],
)
def test_aggregation_by_rating_binning(mock_submission, ratings, expected_bins) -> None:
    """Test if rating are correctly binned."""

    submissions = []
    for i, r in enumerate(ratings):
        submissions.append(
            mock_submission(
                contest_id=1, index=str(i), name=f"Problem {i}", rating=r, tags=[], is_solved=False
            )
        )

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", submissions)

    for rating_bin, count in expected_bins.items():
        stat = next(s for s in analysis.ratings_stats if s.rating == rating_bin)

        assert stat.problem_count == count


@pytest.mark.parametrize("invalid_rating", [None, 0, -100])
def test_unrated_problems_skipped_in_rating_stats(mock_submission, invalid_rating) -> None:
    """Test that unrated problems (rating=None/0) are excluded from rating stats."""

    submissions = [
        mock_submission(
            contest_id=1,
            index="A",
            name="Unrated Problem",
            rating=invalid_rating,
            tags=[],
            is_solved=False,
        )
    ]

    analysis = AbandonedProblemsService.analyze_abandoned_problems("test user", submissions)

    assert analysis.total_abandoned == 1
    assert len(analysis.ratings_stats) == 0
