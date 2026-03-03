"""Division problems API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from backend.api.schemas.base import BaseAPISchema


class DivisionStatsSchema(BaseAPISchema):
    """Schema for statistics of a single division."""

    division: str = Field(..., description="Division name (e.g., 'Div. 1', 'Div. 2')")
    contest_count: int = Field(..., description="Number of contests participated in this division")
    total_problems_solved: int = Field(
        ..., description="Total problems solved in this division"
    )
    average_problems_per_contest: float = Field(
        ..., description="Average number of problems solved per contest in this division"
    )


class DivisionProblemsResponse(BaseAPISchema):
    """Response schema for division problems analysis."""

    divisions: List[DivisionStatsSchema] = Field(
        ..., description="Statistics for each division"
    )
    total_contests: int = Field(
        ..., description="Total number of rated contests participated"
    )
    total_problems_solved: int = Field(
        ..., description="Total number of problems solved across all divisions"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
