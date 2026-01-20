"""Difficulty progression API routes."""

from datetime import datetime
from typing import Optional

from litestar import get
from litestar.response import Response

from sources.api.deps import (
    codeforces_data_service_dependency,
    difficulty_progression_service_dependency,
)
from sources.api.routes.base import BaseMetricController
from sources.api.schemas.difficulty_progression import (
    DifficultyPointSchema,
    DifficultyProgressionResponse,
    GrowthRateSchema,
)
from sources.domain.services.difficulty_progression_service import (
    DifficultyProgressionService,
)
from sources.services.codeforces_data_service import CodeforcesDataService


class DifficultyProgressionController(BaseMetricController):
    """Controller for difficulty progression endpoints."""

    path = "/difficulty-progression"
    tags = ["Difficulty Progression"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "progression_service": difficulty_progression_service_dependency,
        },
    )
    async def get_difficulty_progression(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        progression_service: DifficultyProgressionService,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Response[DifficultyProgressionResponse]:
        """
        Get user's difficulty progression over time.

        Analyzes how problem difficulty has evolved for the user within the specified date range,
        showing monthly and quarterly progression with growth rates.

        Args:
            handle: Codeforces handle
            start_date: Optional start date/time (inclusive) - only analyze problems solved on or after this date. Format: ISO 8601 (e.g., 2024-01-01 or 2024-01-01T12:00:00)
            end_date: Optional end date/time (inclusive) - only analyze problems solved on or before this date. Format: ISO 8601 (e.g., 2024-12-31 or 2024-12-31T23:59:59)

        Returns:
            Difficulty progression analysis with growth metrics for the specified period
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)
        submissions = self._filter_by_date_range(submissions, start_date, end_date)
        self._validate_submissions_exist(submissions, handle)

        progression = progression_service.analyze_difficulty_progression(handle, submissions)

        response = DifficultyProgressionResponse(
            monthly_progression=[
                DifficultyPointSchema.model_validate(point)
                for point in progression.monthly_progression
            ],
            quarterly_progression=[
                DifficultyPointSchema.model_validate(point)
                for point in progression.quarterly_progression
            ],
            growth_rates=[
                GrowthRateSchema.model_validate(rate) for rate in progression.growth_rates
            ],
            total_solved=progression.total_solved,
            periods_analyzed=progression.periods_analyzed,
            first_solve_date=progression.first_solve_date,
            latest_solve_date=progression.latest_solve_date,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)
