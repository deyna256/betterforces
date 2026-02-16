"""Daily activity API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from backend.api.schemas.base import BaseAPISchema


class DailyActivityItemSchema(BaseAPISchema):
    """Schema for a single day's activity."""

    date: str = Field(..., description="Time bucket label (format depends on granularity)")
    solved_count: int = Field(..., description="Number of unique problems solved")
    attempt_count: int = Field(..., description="Number of failed submissions")


class DailyActivityResponse(BaseAPISchema):
    """Response schema for daily activity analysis."""

    days: List[DailyActivityItemSchema] = Field(
        ..., description="Per-day activity data"
    )
    total_solved: int = Field(..., description="Total unique problems solved")
    total_attempts: int = Field(..., description="Total failed submissions")
    active_days: int = Field(..., description="Number of days with any activity")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
