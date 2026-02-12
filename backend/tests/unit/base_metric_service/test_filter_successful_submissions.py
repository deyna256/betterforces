from backend.domain.services import BaseMetricService


def test_filter_successful_submissions_happy_path(mock_submission):
    submission1 = mock_submission(
        contest_id=1,
        index='1',
        name="submission1",
        rating=800,
        tags=['tag'],
        is_solved=False,
    )

    submission2 = mock_submission(
        contest_id=2,
        index='2',
        name="submission2",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    submission3 = mock_submission(
        contest_id=3,
        index='3',
        name="submission3",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    result = BaseMetricService._filter_successful_submissions([submission1, submission2, submission3])

    assert result == [submission2, submission3]

def test_filter_successful_submissions_no_submissions(mock_submission):
    result = BaseMetricService._filter_successful_submissions([])
    assert result == []

def test_filter_successful_submissions_only_not_solved_submissions(mock_submission):
    submission1 = mock_submission(
        contest_id=1,
        index='1',
        name="submission1",
        rating=800,
        tags=['tag'],
        is_solved=False,
    )

    submission2 = mock_submission(
        contest_id=2,
        index='2',
        name="submission2",
        rating=900,
        tags=['tag'],
        is_solved=False,
    )

    submission3 = mock_submission(
        contest_id=1,
        index='1',
        name="submission3",
        rating=900,
        tags=['tag'],
        is_solved=False,
    )

    result = BaseMetricService._filter_successful_submissions([submission1, submission2, submission3])

    assert result == []

def test_filter_successful_submissions_only_solved_submissions(mock_submission):
    submission1 = mock_submission(
        contest_id=1,
        index='1',
        name="submission1",
        rating=800,
        tags=['tag'],
        is_solved=True,
    )

    submission2 = mock_submission(
        contest_id=2,
        index='2',
        name="submission2",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    submission3 = mock_submission(
        contest_id=1,
        index='1',
        name="submission3",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    result = BaseMetricService._filter_successful_submissions([submission1, submission2, submission3])

    assert result == [submission1, submission2, submission3]

def test_filter_successful_submissions_one_solved_submission_to_the_problem(mock_submission):
    submission1 = mock_submission(
        contest_id=1,
        index='1',
        name="submission1",
        rating=800,
        tags=['tag'],
        is_solved=False,
    )

    submission2 = mock_submission(
        contest_id=1,
        index='1',
        name="submission2",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    submission3 = mock_submission(
        contest_id=1,
        index='1',
        name="submission3",
        rating=900,
        tags=['tag'],
        is_solved=False,
    )

    result = BaseMetricService._filter_successful_submissions([submission1, submission2, submission3])

    assert result == [submission2]

