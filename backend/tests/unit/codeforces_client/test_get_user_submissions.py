"""Unit tests for CodeforcesClient.get_user_submissions method."""

import pytest
import httpx
import json
from unittest.mock import AsyncMock, MagicMock

from backend.infrastructure.codeforces_client import (
    CodeforcesAPIError,
    UserNotFoundError,
)
from backend.domain.models.codeforces import Submission, SubmissionStatus


@pytest.mark.asyncio
async def test_get_user_submissions_success(
    codeforces_client, mock_httpx_client, sample_api_response_success
):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response_success
    mock_response.status_code = 200
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    result = await codeforces_client.get_user_submissions("tourist")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(submission, Submission) for submission in result)
    assert result[0].id == 123456789
    assert result[0].verdict == SubmissionStatus.OK
    assert result[0].problem.name == "Test Problem"
    assert result[1].verdict == SubmissionStatus.WRONG_ANSWER
    mock_httpx_client.get.assert_called_once_with(
        "https://codeforces.com/api/user.status", params={"handle": "tourist"}
    )


@pytest.mark.asyncio
async def test_get_user_submissions_empty_result(
    codeforces_client, mock_httpx_client, sample_api_response_empty
):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response_empty
    mock_response.status_code = 200
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    result = await codeforces_client.get_user_submissions("newuser")

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_user_submissions_user_not_found(
    codeforces_client, mock_httpx_client, sample_api_response_user_not_found
):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response_user_not_found
    mock_response.status_code = 400
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(UserNotFoundError) as exc_info:
        await codeforces_client.get_user_submissions("nonexistent")

    assert "not found" in str(exc_info.value)
    assert "nonexistent" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_submissions_user_not_found_variant(
    codeforces_client, mock_httpx_client, sample_api_response_user_not_found_variant
):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response_user_not_found_variant
    mock_response.status_code = 400
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(UserNotFoundError) as exc_info:
        await codeforces_client.get_user_submissions("test")

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_submissions_user_not_found_does_not_have(
    codeforces_client, mock_httpx_client
):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": "FAILED",
        "comment": "User with handle test does not have submissions",
    }
    mock_response.status_code = 400
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(UserNotFoundError):
        await codeforces_client.get_user_submissions("test")


@pytest.mark.asyncio
async def test_get_user_submissions_generic_api_error(
    codeforces_client, mock_httpx_client, sample_api_response_generic_error
):
    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response_generic_error
    mock_response.status_code = 500
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(CodeforcesAPIError) as exc_info:
        await codeforces_client.get_user_submissions("someuser")

    assert "FAILED" in str(exc_info.value)
    assert "Internal server error" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_user_submissions_http_status_error(codeforces_client, mock_httpx_client):
    error_response = MagicMock()
    error_response.status_code = 503
    error_response.text = "Service Unavailable"
    mock_httpx_client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError("503 Error", request=MagicMock(), response=error_response)
    )

    with pytest.raises(CodeforcesAPIError) as exc_info:
        await codeforces_client.get_user_submissions("user")

    assert "HTTP error 503" in str(exc_info.value)
    assert "Service Unavailable" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_submissions_request_error(codeforces_client, mock_httpx_client):
    mock_httpx_client.get = AsyncMock(side_effect=httpx.RequestError("Connection timeout"))

    with pytest.raises(CodeforcesAPIError) as exc_info:
        await codeforces_client.get_user_submissions("user")

    assert "Request error" in str(exc_info.value)
    assert "Connection timeout" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_submissions_json_decode_error(codeforces_client, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(CodeforcesAPIError) as exc_info:
        await codeforces_client.get_user_submissions("user")

    assert "JSON decode error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_submissions_missing_status_field(codeforces_client, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": []}
    mock_response.status_code = 200
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    with pytest.raises(CodeforcesAPIError):
        await codeforces_client.get_user_submissions("user")


@pytest.mark.asyncio
async def test_get_user_submissions_correct_url_construction(codeforces_client, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "OK", "result": []}
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    await codeforces_client.get_user_submissions("testuser")

    call_args = mock_httpx_client.get.call_args
    assert call_args[0][0] == "https://codeforces.com/api/user.status"
    assert call_args[1]["params"] == {"handle": "testuser"}
