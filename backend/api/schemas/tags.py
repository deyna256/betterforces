"""Tags API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from backend.api.schemas.base import BaseAPISchema


class SimpleTagInfoSchema(BaseAPISchema):
    """Schema for a single tag information (simplified version)."""

    tag: str = Field(..., description="The tag name")
    average_rating: float = Field(
        ..., description="Average rating of all solved problems with this tag"
    )
    median_rating: float = Field(
        ..., description="Median rating of all solved problems with this tag"
    )
    problem_count: int = Field(..., description="Number of solved problems with this tag")


class TagInfoSchema(SimpleTagInfoSchema):
    """Schema for a single tag information (detailed version for weak tags)."""

    problems: List[str] = Field(..., description="Names of solved problems with this tag")


class TagsResponse(BaseAPISchema):
    """Response schema for tags analysis."""

    tags: List[SimpleTagInfoSchema] = Field(..., description="List of tags analysis")
    overall_average_rating: float = Field(
        ..., description="Overall average rating of all solved problems"
    )
    overall_median_rating: float = Field(
        ..., description="Overall median rating of all solved problems"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")


class WeakTagsResponse(BaseAPISchema):
    """Response schema for weak tags analysis."""

    weak_tags: List[SimpleTagInfoSchema] = Field(
        ..., description="List of weak tags (significantly lower average rating)"
    )
    overall_average_rating: float = Field(
        ..., description="Overall average rating of all solved problems"
    )
    overall_median_rating: float = Field(
        ..., description="Overall median rating of all solved problems"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    threshold_used: int = Field(
        ..., description="Rating difference threshold used to identify weak tags"
    )
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
