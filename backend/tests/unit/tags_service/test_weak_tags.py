from backend.domain.models.tags import TagInfo, TagsAnalysis


def test_returns_no_weak_tags_when_tags_list_is_empty() -> None:
    analysis = TagsAnalysis(
        handle="test_user",
        tags=[],
        overall_average_rating=1400.0,
        overall_median_rating=1400.0,
        total_solved=0,
    )

    weak_tags = analysis.get_weak_tags()

    assert weak_tags == []


def test_returns_no_weak_tags_when_total_solved_is_zero() -> None:
    analysis = TagsAnalysis(
        handle="test_user",
        tags=[],
        overall_average_rating=0.0,
        overall_median_rating=0.0,
        total_solved=0,
    )

    weak_tags = analysis.get_weak_tags()

    assert weak_tags == []


def test_returns_no_weak_tags_when_all_tags_are_within_threshold() -> None:
    analysis = TagsAnalysis(
        handle="test_user",
        tags=[
            TagInfo(
                tag="implementation",
                average_rating=1380.0,
                median_rating=1350.0,
                problem_count=10,
                problems=["Problem A"],
            ),
            TagInfo(
                tag="math",
                average_rating=1350.0,
                median_rating=1340.0,
                problem_count=8,
                problems=["Problem B"],
            ),
            TagInfo(
                tag="greedy",
                average_rating=1250.0,
                median_rating=1240.0,
                problem_count=5,
                problems=["Problem C"],
            ),
        ],
        overall_average_rating=1400.0,
        overall_median_rating=1380.0,
        total_solved=23,
    )

    # Default threshold is 200, all tags have diff < 200
    weak_tags = analysis.get_weak_tags()

    assert weak_tags == []


def test_returns_all_tags_when_every_tag_is_below_overall_rating_by_threshold() -> None:
    tag1 = TagInfo(
        tag="graphs",
        average_rating=900.0,
        median_rating=850.0,
        problem_count=3,
        problems=["Problem A"],
    )
    tag2 = TagInfo(
        tag="dp",
        average_rating=800.0,
        median_rating=750.0,
        problem_count=2,
        problems=["Problem B"],
    )
    tag3 = TagInfo(
        tag="geometry",
        average_rating=700.0,
        median_rating=650.0,
        problem_count=1,
        problems=["Problem C"],
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[tag1, tag2, tag3],
        overall_average_rating=1400.0,
        overall_median_rating=1350.0,
        total_solved=6,
    )

    weak_tags = analysis.get_weak_tags()

    assert len(weak_tags) == 3
    # All tags should be present
    weak_tag_names = [t.tag for t in weak_tags]
    assert "graphs" in weak_tag_names
    assert "dp" in weak_tag_names
    assert "geometry" in weak_tag_names


def test_applies_custom_threshold_when_filtering_weak_tags() -> None:
    tag_a = TagInfo(
        tag="tag_a",
        average_rating=1250.0,
        median_rating=1240.0,
        problem_count=5,
        problems=["Problem A"],
    )
    tag_b = TagInfo(
        tag="tag_b",
        average_rating=1150.0,
        median_rating=1140.0,
        problem_count=3,
        problems=["Problem B"],
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[tag_a, tag_b],
        overall_average_rating=1500.0,
        overall_median_rating=1480.0,
        total_solved=8,
    )

    # With threshold=300, only tag_b is weak (diff=350)
    # tag_a has diff=250, which is less than 300
    weak_tags = analysis.get_weak_tags(threshold_diff=300)

    assert len(weak_tags) == 1
    assert weak_tags[0].tag == "tag_b"


def test_includes_tags_at_or_below_default_threshold_difference() -> None:
    tag_not_weak = TagInfo(
        tag="just_above",
        average_rating=1001.0,
        median_rating=1000.0,
        problem_count=5,
        problems=["Problem A"],
    )
    tag_weak_exactly = TagInfo(
        tag="exactly_threshold",
        average_rating=1000.0,
        median_rating=990.0,
        problem_count=4,
        problems=["Problem B"],
    )
    tag_weak_below = TagInfo(
        tag="below_threshold",
        average_rating=800.0,
        median_rating=750.0,
        problem_count=3,
        problems=["Problem C"],
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[tag_not_weak, tag_weak_exactly, tag_weak_below],
        overall_average_rating=1200.0,
        overall_median_rating=1180.0,
        total_solved=12,
    )

    weak_tags = analysis.get_weak_tags()  # Default threshold=200

    assert len(weak_tags) == 2
    weak_tag_names = [t.tag for t in weak_tags]
    assert "just_above" not in weak_tag_names  # diff=199
    assert "exactly_threshold" in weak_tag_names  # diff=200
    assert "below_threshold" in weak_tag_names  # diff=400


def test_sorts_weak_tags_by_rating_difference_descending() -> None:
    tag_a = TagInfo(
        tag="tag_a",
        average_rating=1100.0,
        median_rating=1080.0,
        problem_count=5,
        problems=["Problem A"],
    )
    tag_b = TagInfo(
        tag="tag_b",
        average_rating=1000.0,
        median_rating=980.0,
        problem_count=4,
        problems=["Problem B"],
    )
    tag_c = TagInfo(
        tag="tag_c",
        average_rating=1200.0,
        median_rating=1180.0,
        problem_count=3,
        problems=["Problem C"],
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[tag_a, tag_b, tag_c],
        overall_average_rating=1500.0,
        overall_median_rating=1480.0,
        total_solved=12,
    )

    weak_tags = analysis.get_weak_tags()

    # All three are weak (diffs: 400, 500, 300)
    # Expected order: tag_b (500), tag_a (400), tag_c (300)
    assert len(weak_tags) == 3
    assert weak_tags[0].tag == "tag_b"  # diff=500
    assert weak_tags[1].tag == "tag_a"  # diff=400
    assert weak_tags[2].tag == "tag_c"  # diff=300


def test_filters_and_sorts_only_weak_tags_from_mixed_strength_tags() -> None:
    implementation = TagInfo(
        tag="implementation",
        average_rating=1400.0,
        median_rating=1380.0,
        problem_count=20,
        problems=["Problem 1"] * 20,
    )
    math = TagInfo(
        tag="math",
        average_rating=1320.0,
        median_rating=1300.0,
        problem_count=15,
        problems=["Problem 2"] * 15,
    )
    graphs = TagInfo(
        tag="graphs",
        average_rating=1100.0,
        median_rating=1080.0,
        problem_count=8,
        problems=["Problem 3"] * 8,
    )
    dp = TagInfo(
        tag="dp",
        average_rating=900.0,
        median_rating=880.0,
        problem_count=5,
        problems=["Problem 4"] * 5,
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[implementation, math, graphs, dp],
        overall_average_rating=1350.0,
        overall_median_rating=1300.0,
        total_solved=48,
    )

    weak_tags = analysis.get_weak_tags()

    # Expected weak tags: graphs (diff=250), dp (diff=450)
    # implementation (diff=-50) and math (diff=30) are NOT weak
    assert len(weak_tags) == 2

    # Should be sorted by difference (dp first with 450, then graphs with 250)
    assert weak_tags[0].tag == "dp"
    assert weak_tags[1].tag == "graphs"


def test_preserves_tag_fields_when_returning_weak_tags() -> None:
    graphs = TagInfo(
        tag="graphs",
        average_rating=1000.0,
        median_rating=980.0,
        problem_count=5,
        problems=["Graph Problem 1", "Graph Problem 2"],
    )

    analysis = TagsAnalysis(
        handle="test_user",
        tags=[graphs],
        overall_average_rating=1400.0,
        overall_median_rating=1380.0,
        total_solved=5,
    )

    weak_tags = analysis.get_weak_tags()

    assert len(weak_tags) == 1
    weak_tag = weak_tags[0]

    # Verify all properties are preserved
    assert weak_tag.tag == "graphs"
    assert weak_tag.average_rating == 1000.0
    assert weak_tag.median_rating == 980.0
    assert weak_tag.problem_count == 5
    assert weak_tag.problems == ["Graph Problem 1", "Graph Problem 2"]
