from backend.domain.services import BaseMetricService


def test_deduplicate_problems_happy_path(mock_submission):
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

    result = BaseMetricService._deduplicate_problems([submission1, submission2])
    assert result == [submission1]