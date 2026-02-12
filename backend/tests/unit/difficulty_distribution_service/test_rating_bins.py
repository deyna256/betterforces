from backend.domain.services.difficulty_distribution_service import DifficultyDistributionService


class TestGetRatingBin:

    def test_returns_same_value_for_exact_bin_boundary(self) -> None:
        assert DifficultyDistributionService._get_rating_bin(800) == 800
        assert DifficultyDistributionService._get_rating_bin(1400) == 1400

    def test_floors_mid_bin_value_to_bin_start(self) -> None:
        assert DifficultyDistributionService._get_rating_bin(850) == 800
        assert DifficultyDistributionService._get_rating_bin(1350) == 1300

    def test_floors_value_just_below_next_bin(self) -> None:
        assert DifficultyDistributionService._get_rating_bin(899) == 800
        assert DifficultyDistributionService._get_rating_bin(1499) == 1400

    def test_floors_low_rating(self) -> None:
        assert DifficultyDistributionService._get_rating_bin(100) == 100

    def test_floors_high_rating(self) -> None:
        assert DifficultyDistributionService._get_rating_bin(3500) == 3500


class TestCreateBinDistribution:

    def test_returns_empty_dict_for_empty_submissions(self) -> None:
        result = DifficultyDistributionService._create_bin_distribution([])
        assert result == {}

    def test_returns_empty_dict_when_all_ratings_are_none(self, mock_submission) -> None:
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

        result = DifficultyDistributionService._create_bin_distribution(submissions)

        assert result == {}

    def test_groups_single_submission_into_correct_bin(self, mock_submission) -> None:
        submissions = [
            mock_submission(
                contest_id=100,
                index="A",
                name="Problem A",
                rating=1350,
                tags=["math"],
                is_solved=True,
            ),
        ]

        result = DifficultyDistributionService._create_bin_distribution(submissions)

        assert result == {1300: 1}

    def test_aggregates_multiple_submissions_in_same_bin(self, mock_submission) -> None:
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

        result = DifficultyDistributionService._create_bin_distribution(submissions)

        assert result == {800: 3}

    def test_creates_separate_bins_for_different_ratings(self, mock_submission) -> None:
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
                tags=["dp"],
                is_solved=True,
            ),
            mock_submission(
                contest_id=100,
                index="C",
                name="Problem C",
                rating=2000,
                tags=["greedy"],
                is_solved=True,
            ),
        ]

        result = DifficultyDistributionService._create_bin_distribution(submissions)

        assert result == {800: 1, 1200: 1, 2000: 1}

    def test_skips_unrated_among_rated_submissions(self, mock_submission) -> None:
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

        result = DifficultyDistributionService._create_bin_distribution(submissions)

        assert result == {800: 1, 1200: 1}
