"""Difficulty distribution API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from backend.api.schemas.base import BaseAPISchema


class RatingRangeSchema(BaseAPISchema):
    """Schema for a single rating range."""

    rating: int = Field(..., description="Rating (e.g., 800, 900, 1000...)")
    problem_count: int = Field(..., description="Number of problems solved at this rating")


class DifficultyDistributionResponse(BaseAPISchema):
    """Response schema for difficulty distribution analysis."""

    ranges: List[RatingRangeSchema] = Field(
        ..., description="List of rating ranges with problem counts"
    )
    total_solved: int = Field(..., description="Total number of unique problems solved")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
