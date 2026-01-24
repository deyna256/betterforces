"""Codeforces data service for BetterForces."""

from typing import List

from backend.infrastructure.codeforces_client import CodeforcesClient, UserNotFoundError
from backend.domain.models.codeforces import Submission


class CodeforcesDataService:
    """Service for fetching user data from Codeforces API."""

    def __init__(self):
        self.codeforces_client = CodeforcesClient()

    async def get_user_submissions(self, handle: str) -> List[Submission]:
        """
        Get user submissions from Codeforces API.

        Args:
            handle: Codeforces handle

        Returns:
            List of user's submissions
        """
        async with self.codeforces_client as client:
            try:
                return await client.get_user_submissions(handle)
            except UserNotFoundError:
                # Re-raise to be caught by controllers
                raise
