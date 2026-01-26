"""Unit tests for Codeforces client custom exceptions."""

import pytest
from backend.infrastructure.codeforces_client import CodeforcesAPIError, UserNotFoundError


def test_codeforces_api_error_with_message_only():
    error_message = "API request failed"

    error = CodeforcesAPIError(error_message)

    assert str(error) == error_message
    assert error.status_code is None


def test_codeforces_api_error_with_status_code():
    error_message = "Internal server error"
    status_code = 500

    error = CodeforcesAPIError(error_message, status_code)

    assert str(error) == error_message
    assert error.status_code == 500


def test_codeforces_api_error_with_none_status_code():
    error_message = "Some error"

    error = CodeforcesAPIError(error_message, status_code=None)

    assert str(error) == error_message
    assert error.status_code is None


def test_codeforces_api_error_is_exception():
    error = CodeforcesAPIError("test error")

    assert isinstance(error, Exception)


def test_codeforces_api_error_can_be_raised():
    with pytest.raises(CodeforcesAPIError) as exc_info:
        raise CodeforcesAPIError("Test error", 400)

    assert str(exc_info.value) == "Test error"
    assert exc_info.value.status_code == 400


def test_codeforces_api_error_status_code_attribute():
    error = CodeforcesAPIError("Error", 404)

    assert hasattr(error, "status_code")
    assert error.status_code == 404


def test_user_not_found_error_basic():
    error_message = "User 'tourist' not found"

    error = UserNotFoundError(error_message)

    assert str(error) == error_message


def test_user_not_found_error_is_exception():
    error = UserNotFoundError("User not found")

    assert isinstance(error, Exception)


def test_user_not_found_error_can_be_raised():
    with pytest.raises(UserNotFoundError) as exc_info:
        raise UserNotFoundError("User 'nonexistent' not found on Codeforces")

    assert "nonexistent" in str(exc_info.value)


def test_user_not_found_error_distinct_from_api_error():
    user_error = UserNotFoundError("User not found")
    api_error = CodeforcesAPIError("API error")

    assert type(user_error) is not type(api_error)
    assert not isinstance(user_error, CodeforcesAPIError)
    assert not isinstance(api_error, UserNotFoundError)


def test_can_catch_user_not_found_separately():
    with pytest.raises(UserNotFoundError):
        raise UserNotFoundError("User not found")

    with pytest.raises(CodeforcesAPIError):
        raise CodeforcesAPIError("API failed")


def test_exceptions_with_empty_message():
    api_error = CodeforcesAPIError("")
    user_error = UserNotFoundError("")

    assert str(api_error) == ""
    assert str(user_error) == ""


def test_codeforces_api_error_with_various_status_codes():
    error_400 = CodeforcesAPIError("Bad Request", 400)
    error_404 = CodeforcesAPIError("Not Found", 404)
    error_500 = CodeforcesAPIError("Internal Server Error", 500)
    error_503 = CodeforcesAPIError("Service Unavailable", 503)

    assert error_400.status_code == 400
    assert error_404.status_code == 404
    assert error_500.status_code == 500
    assert error_503.status_code == 503


def test_codeforces_api_error_message_formatting():
    status = "FAILED"
    comment = "handle: User with handle test not found"
    status_code = 400

    error = CodeforcesAPIError(
        f"API returned status: {status}. Comment: {comment}", status_code
    )

    assert "FAILED" in str(error)
    assert "not found" in str(error)
    assert error.status_code == 400


def test_exceptions_inheritance():
    api_error = CodeforcesAPIError("test")
    user_error = UserNotFoundError("test")

    assert isinstance(api_error, Exception)
    assert isinstance(user_error, Exception)
    assert isinstance(api_error, BaseException)
    assert isinstance(user_error, BaseException)
