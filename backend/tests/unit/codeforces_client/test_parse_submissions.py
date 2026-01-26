"""Unit tests for CodeforcesClient._parse_submissions method."""

from backend.domain.models.codeforces import SubmissionStatus


def test_parse_submissions_success(codeforces_client, sample_submission_data):
    result = codeforces_client._parse_submissions(sample_submission_data)

    assert len(result) == 2

    assert result[0].id == 123456789
    assert result[0].contest_id == 1000
    assert result[0].creation_time_seconds == 1609459200
    assert result[0].programming_language == "Python 3"
    assert result[0].verdict == SubmissionStatus.OK

    assert result[0].problem.contest_id == 1000
    assert result[0].problem.index == "A"
    assert result[0].problem.name == "Test Problem"
    assert result[0].problem.rating == 800
    assert result[0].problem.tags == ["implementation", "math"]

    assert result[1].id == 987654321
    assert result[1].verdict == SubmissionStatus.WRONG_ANSWER
    assert result[1].problem.name == "Another Problem"


def test_parse_submissions_empty_list(codeforces_client):
    result = codeforces_client._parse_submissions([])

    assert result == []


def test_parse_submissions_with_missing_optional_fields(
    codeforces_client, sample_submission_with_missing_fields
):
    result = codeforces_client._parse_submissions(sample_submission_with_missing_fields)

    assert len(result) == 1
    assert result[0].id == 111111111
    assert result[0].problem.name == "No Rating Problem"
    assert result[0].problem.rating is None
    assert result[0].problem.tags == []
    assert result[0].verdict == SubmissionStatus.COMPILATION_ERROR


def test_parse_submissions_with_unknown_verdict(
    codeforces_client, sample_submission_with_unknown_verdict
):
    result = codeforces_client._parse_submissions(sample_submission_with_unknown_verdict)

    assert len(result) == 1
    assert result[0].id == 222222222
    assert result[0].verdict == SubmissionStatus.WRONG_ANSWER
    assert result[0].problem.name == "Test"


def test_parse_submissions_skips_malformed_entries(codeforces_client, sample_malformed_submission):
    result = codeforces_client._parse_submissions(sample_malformed_submission)

    assert len(result) == 2
    assert result[0].id == 333333333
    assert result[0].contest_id == 0
    assert result[0].creation_time_seconds == 0
    assert result[1].id == 0
    assert result[1].problem.contest_id == 0


def test_parse_submissions_mixed_valid_and_invalid(codeforces_client, sample_submission_data):
    mixed_data = [
        sample_submission_data[0],
        {"invalid": "data"},
        sample_submission_data[1],
    ]

    result = codeforces_client._parse_submissions(mixed_data)

    assert len(result) == 3
    assert result[0].id == 123456789
    assert result[1].id == 0
    assert result[2].id == 987654321


def test_parse_submissions_problem_defaults(codeforces_client):
    data = [
        {
            "id": 12345,
            "contestId": 100,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "C++",
            "verdict": "OK",
            "problem": {},
        }
    ]

    result = codeforces_client._parse_submissions(data)

    assert len(result) == 1
    assert result[0].problem.contest_id == 0
    assert result[0].problem.index == ""
    assert result[0].problem.name == ""
    assert result[0].problem.rating is None


def test_parse_submissions_all_verdict_types(codeforces_client):
    verdicts = [
        "OK",
        "WRONG_ANSWER",
        "TIME_LIMIT_EXCEEDED",
        "MEMORY_LIMIT_EXCEEDED",
        "RUNTIME_ERROR",
        "COMPILATION_ERROR",
        "IDLENESS_LIMIT_EXCEEDED",
    ]
    data = [
        {
            "id": i,
            "contestId": 100,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "Python",
            "verdict": verdict,
            "problem": {"contestId": 100, "index": "A", "name": "Test"},
        }
        for i, verdict in enumerate(verdicts)
    ]

    result = codeforces_client._parse_submissions(data)

    assert len(result) == len(verdicts)
    for i, verdict in enumerate(verdicts):
        assert result[i].verdict == SubmissionStatus(verdict)


def test_parse_submissions_problem_with_no_tags(codeforces_client):
    data = [
        {
            "id": 999,
            "contestId": 200,
            "creationTimeSeconds": 1700000000,
            "programmingLanguage": "Java",
            "verdict": "OK",
            "problem": {
                "contestId": 200,
                "index": "Z",
                "name": "Problem without tags",
                "rating": 2000,
            },
        }
    ]

    result = codeforces_client._parse_submissions(data)

    assert len(result) == 1
    assert result[0].problem.tags == []


def test_parse_submissions_preserves_order(codeforces_client, sample_submission_data):
    result = codeforces_client._parse_submissions(sample_submission_data)

    assert result[0].id == sample_submission_data[0]["id"]
    assert result[1].id == sample_submission_data[1]["id"]


def test_parse_submissions_submission_defaults(codeforces_client):
    data = [
        {
            "problem": {"contestId": 100, "index": "A", "name": "Test"},
        }
    ]

    result = codeforces_client._parse_submissions(data)

    assert len(result) == 1
    assert result[0].id == 0
    assert result[0].contest_id == 0
    assert result[0].creation_time_seconds == 0
    assert result[0].programming_language == ""


def test_parse_submissions_problem_key_property(codeforces_client):
    data = [
        {
            "id": 111,
            "contestId": 1500,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "Python",
            "verdict": "OK",
            "problem": {"contestId": 1500, "index": "B", "name": "Test"},
        }
    ]

    result = codeforces_client._parse_submissions(data)

    assert result[0].problem.problem_key == "1500B"


def test_parse_submissions_is_solved_property(codeforces_client):
    data = [
        {
            "id": 1,
            "contestId": 100,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "C++",
            "verdict": "OK",
            "problem": {"contestId": 100, "index": "A", "name": "Solved"},
        },
        {
            "id": 2,
            "contestId": 100,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "C++",
            "verdict": "WRONG_ANSWER",
            "problem": {"contestId": 100, "index": "B", "name": "Not Solved"},
        },
    ]

    result = codeforces_client._parse_submissions(data)

    assert result[0].is_solved is True
    assert result[1].is_solved is False
