"""Rating distribution API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from sources.api.schemas.base import BaseAPISchema


class RatingPointSchema(BaseAPISchema):
    """Schema for a single rating point in the distribution."""

    timestamp: int = Field(..., description="Unix timestamp when the problem was solved")
    rating: int = Field(..., description="Problem rating that was solved")
    problem_name: str = Field(..., description="Name of the solved problem")
    date: str = Field(..., description="Human-readable date string")


class RatingDistributionResponse(BaseAPISchema):
    """Response schema for rating distribution over time."""

    handle: str = Field(..., description="Codeforces handle")
    rating_points: List[RatingPointSchema] = Field(
        ..., description="Chronological list of solved problems with ratings"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
