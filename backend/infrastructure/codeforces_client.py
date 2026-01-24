"""Codeforces API client for BetterForces."""

import httpx
from typing import List, Dict, Any
import json
from backend.config import settings
from backend.domain.models.codeforces import Submission, Problem, SubmissionStatus


class CodeforcesAPIError(Exception):
    """Exception raised when Codeforces API returns an error."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class UserNotFoundError(Exception):
    """Exception raised when user is not found on Codeforces."""
    pass


class CodeforcesClient:
    """Client for interacting with Codeforces API."""

    def __init__(self):
        self.base_url = settings.codeforces_api_base.rstrip("/")
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.http_client.aclose()

    async def get_user_submissions(self, handle: str) -> List[Submission]:
        """
        Fetch all submissions for a user.

        Args:
            handle: Codeforces handle

        Returns:
            List of user's submissions

        Raises:
            CodeforcesAPIError: If API request fails
        """
        url = f"{self.base_url}/user.status"

        try:
            response = await self.http_client.get(url, params={"handle": handle})

            data = response.json()

            # Check API response status
            status = data.get("status")
            result = data.get("result", [])
            comment = data.get("comment", "")

            if status != "OK":
                # Check for user not found cases
                if "handle: User with handle" in comment and ("not found" in comment or "does not exist" in comment):
                    raise UserNotFoundError(f"User '{handle}' not found on Codeforces")
                # Check for specific error messages indicating user not found
            if "User with handle" in comment and ("not found" in comment or "does not exist" in comment or "does not have" in comment):
                raise UserNotFoundError(f"User '{handle}' not found on Codeforces")
            raise CodeforcesAPIError(f"API returned status: {status}. Comment: {comment}", response.status_code)

            # Empty result means no submissions, but user exists
            return self._parse_submissions(result)

        except httpx.HTTPStatusError as e:
            raise CodeforcesAPIError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise CodeforcesAPIError(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            raise CodeforcesAPIError(f"JSON decode error: {str(e)}")

    def _parse_submissions(self, raw_submissions: List[Dict[str, Any]]) -> List[Submission]:
        """Parse raw API response into Submission objects."""
        submissions = []

        for raw_submission in raw_submissions:
            try:
                # Parse problem
                raw_problem = raw_submission.get("problem", {})
                problem = Problem(
                    contest_id=raw_problem.get("contestId", 0),
                    index=raw_problem.get("index", ""),
                    name=raw_problem.get("name", ""),
                    rating=raw_problem.get("rating"),
                    tags=raw_problem.get("tags", []),
                )

                # Parse verdict
                verdict_str = raw_submission.get("verdict", "")
                try:
                    verdict = SubmissionStatus(verdict_str)
                except ValueError:
                    # Unknown verdict, treat as failed
                    verdict = SubmissionStatus.WRONG_ANSWER

                submission = Submission(
                    id=raw_submission.get("id", 0),
                    contest_id=raw_submission.get("contestId", 0),
                    creation_time_seconds=raw_submission.get("creationTimeSeconds", 0),
                    problem=problem,
                    verdict=verdict,
                    programming_language=raw_submission.get("programmingLanguage", ""),
                )

                submissions.append(submission)

            except (KeyError, TypeError):
                # Skip malformed submissions
                continue

        return submissions
