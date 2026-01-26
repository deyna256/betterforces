"""Fixtures for Codeforces client unit tests."""

import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from backend.infrastructure.codeforces_client import CodeforcesClient


@pytest.fixture
def mock_httpx_client():
    mock_client = AsyncMock()
    mock_client.aclose = AsyncMock()
    return mock_client


@pytest.fixture
def codeforces_client(mock_httpx_client):
    with patch("backend.infrastructure.codeforces_client.httpx.AsyncClient") as mock:
        mock.return_value = mock_httpx_client
        client = CodeforcesClient()
        yield client


@pytest.fixture
def sample_submission_data() -> List[Dict[str, Any]]:
    return [
        {
            "id": 123456789,
            "contestId": 1000,
            "creationTimeSeconds": 1609459200,
            "programmingLanguage": "Python 3",
            "verdict": "OK",
            "problem": {
                "contestId": 1000,
                "index": "A",
                "name": "Test Problem",
                "rating": 800,
                "tags": ["implementation", "math"],
            },
        },
        {
            "id": 987654321,
            "contestId": 1001,
            "creationTimeSeconds": 1609545600,
            "programmingLanguage": "C++17",
            "verdict": "WRONG_ANSWER",
            "problem": {
                "contestId": 1001,
                "index": "B",
                "name": "Another Problem",
                "rating": 1200,
                "tags": ["dp", "greedy"],
            },
        },
    ]


@pytest.fixture
def sample_api_response_success(sample_submission_data) -> Dict[str, Any]:
    return {"status": "OK", "result": sample_submission_data}


@pytest.fixture
def sample_api_response_empty() -> Dict[str, Any]:
    return {"status": "OK", "result": []}


@pytest.fixture
def sample_api_response_user_not_found() -> Dict[str, Any]:
    return {
        "status": "FAILED",
        "comment": "handle: User with handle nonexistent not found",
    }


@pytest.fixture
def sample_api_response_user_not_found_variant() -> Dict[str, Any]:
    return {
        "status": "FAILED",
        "comment": "User with handle test does not exist",
    }


@pytest.fixture
def sample_api_response_generic_error() -> Dict[str, Any]:
    return {
        "status": "FAILED",
        "comment": "Internal server error",
    }


@pytest.fixture
def sample_submission_with_missing_fields() -> List[Dict[str, Any]]:
    return [
        {
            "id": 111111111,
            "contestId": 500,
            "creationTimeSeconds": 1600000000,
            "programmingLanguage": "Java 11",
            "verdict": "COMPILATION_ERROR",
            "problem": {
                "contestId": 500,
                "index": "C",
                "name": "No Rating Problem",
            },
        }
    ]


@pytest.fixture
def sample_submission_with_unknown_verdict() -> List[Dict[str, Any]]:
    return [
        {
            "id": 222222222,
            "contestId": 600,
            "creationTimeSeconds": 1610000000,
            "programmingLanguage": "PyPy 3",
            "verdict": "UNKNOWN_VERDICT_TYPE",
            "problem": {
                "contestId": 600,
                "index": "D",
                "name": "Test",
                "rating": 1500,
                "tags": ["graphs"],
            },
        }
    ]


@pytest.fixture
def sample_malformed_submission() -> List[Dict[str, Any]]:
    return [
        {
            "id": 333333333,
            "problem": {
                "contestId": 700,
                "index": "E",
            },
        },
        {
            "random_field": "value",
        },
    ]
