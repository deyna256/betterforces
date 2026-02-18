from backend.domain.services.base import SubmissionProcessor


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

    processor = SubmissionProcessor([submission1, submission2])
    result = processor._deduplicate_problems()
    assert result == [submission1]

def test_deduplicate_problems_empty_submissions_list(mock_submission):
   processor = SubmissionProcessor([])
   result = processor._deduplicate_problems()
   assert result == []

def test_deduplicate_problems_single_submission(mock_submission):
   submission1 = mock_submission(
       contest_id=1,
       index='1',
       name="submission1",
       rating=800,
       tags=['tag'],
       is_solved=False,
   )

   processor = SubmissionProcessor([submission1])
   result = processor._deduplicate_problems()

   assert result == [submission1]

def test_deduplicate_problems_all_unique_submissions(mock_submission):
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

    processor = SubmissionProcessor([submission1, submission2, submission3])
    result = processor._deduplicate_problems()

    assert result == [submission1, submission2, submission3]

def test_deduplicate_problems_multiple_duplicates(mock_submission):
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
        rating=800,
        tags=['tag'],
        is_solved=False,
    )

    processor = SubmissionProcessor([submission1, submission2, submission3])
    result = processor._deduplicate_problems()

    assert result == [submission1]

def test_deduplicate_problems_preserves_order(mock_submission):
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
        contest_id=1,
        index='1',
        name="submission3",
        rating=800,
        tags=['tag'],
        is_solved=False,
    )

    processor = SubmissionProcessor([submission1, submission2, submission3])
    result = processor._deduplicate_problems()

    assert result == [submission1, submission2]

def test_deduplicate_problems_same_index_different_contest_id(mock_submission):
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
        index='1',
        name="submission2",
        rating=900,
        tags=['tag'],
        is_solved=True,
    )

    processor = SubmissionProcessor([submission1, submission2])
    result = processor._deduplicate_problems()
    assert result == [submission1, submission2]

def test_deduplicate_problems_different_index_same_contest_id(mock_submission):

    submission1 = mock_submission(
        contest_id=1,
        index='2',
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

    processor = SubmissionProcessor([submission1, submission2])
    result = processor._deduplicate_problems()
    assert result == [submission1, submission2]
