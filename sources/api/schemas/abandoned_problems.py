"""Abandoned problems API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from sources.api.schemas.base import BaseAPISchema


class TagAbandonedSchema(BaseAPISchema):
    """Schema for abandoned problems statistics by tag."""

    tag: str = Field(..., description="Tag name")
    problem_count: int = Field(..., description="Number of abandoned problems with this tag")
    total_failed_attempts: int = Field(
        ..., description="Total number of failed submission attempts for this tag"
    )


class RatingAbandonedSchema(BaseAPISchema):
    """Schema for abandoned problems statistics by rating."""

    rating: int = Field(..., description="Rating bin (e.g., 800, 900, 1000...)")
    problem_count: int = Field(..., description="Number of abandoned problems at this rating")
    total_failed_attempts: int = Field(
        ..., description="Total number of failed submission attempts at this rating"
    )


class AbandonedProblemDetailsSchema(BaseAPISchema):
    """Schema for detailed information about an abandoned problem."""

    contest_id: int = Field(..., description="Contest ID where the problem is from")
    index: str = Field(..., description="Problem index within the contest")
    name: str = Field(..., description="Problem name")
    rating: int = Field(..., description="Problem rating (0 if unrated)")
    tags: List[str] = Field(..., description="Tags for this problem")
    failed_attempts: int = Field(..., description="Number of failed attempts on this problem")


class AbandonedProblemByTagsResponse(BaseAPISchema):
    """Response schema for abandoned problems analysis by tags."""

    tags: List[TagAbandonedSchema] = Field(..., description="Abandoned problems grouped by tags")
    total_abandoned_problems: int = Field(
        ..., description="Total number of unique abandoned problems"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")


class AbandonedProblemByRatingsResponse(BaseAPISchema):
    """Response schema for abandoned problems analysis by ratings."""

    ratings: List[RatingAbandonedSchema] = Field(
        ..., description="Abandoned problems grouped by rating bins"
    )
    total_abandoned_problems: int = Field(
        ..., description="Total number of unique abandoned problems"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")


class AbandonedProblemsDetailsResponse(BaseAPISchema):
    """Response schema for detailed abandoned problems list."""

    problems: List[AbandonedProblemDetailsSchema] = Field(
        ..., description="List of detailed information about abandoned problems"
    )
    total_abandoned: int = Field(..., description="Total number of abandoned problems")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
