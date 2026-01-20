"""Difficulty progression API schemas."""

from datetime import datetime
from typing import List

from pydantic import Field

from sources.api.schemas.base import BaseAPISchema


class DifficultyPointSchema(BaseAPISchema):
    """Schema for difficulty progression data point."""

    date_month: str = Field(..., description="Month in YYYY-MM format")
    date_quarter: str = Field(..., description="Quarter in YYYY-Q format")
    average_rating: float = Field(
        ..., description="Average rating of problems solved in this period"
    )
    problem_count: int = Field(..., description="Number of rated problems solved in this period")
    period_start: datetime = Field(..., description="Start timestamp of this period")
    period_end: datetime = Field(..., description="End timestamp of this period")


class GrowthRateSchema(BaseAPISchema):
    """Schema for growth rate calculation between two periods."""

    from_period: str = Field(..., description="From period (YYYY-MM or YYYY-Q)")
    to_period: str = Field(..., description="To period (YYYY-MM or YYYY-Q)")
    rating_change: float = Field(..., description="Change in average rating")
    monthly_growth: float = Field(..., description="Average monthly growth rate")
    months_difference: int = Field(..., description="Number of months between periods")


class DifficultyProgressionResponse(BaseAPISchema):
    """Response schema for difficulty progression analysis."""

    monthly_progression: List[DifficultyPointSchema] = Field(
        ..., description="Monthly difficulty progression data"
    )
    quarterly_progression: List[DifficultyPointSchema] = Field(
        ..., description="Quarterly difficulty progression data"
    )
    growth_rates: List[GrowthRateSchema] = Field(
        ..., description="Calculated growth rates between periods"
    )
    total_solved: int = Field(..., description="Total number of problems solved")
    periods_analyzed: int = Field(..., description="Number of time periods analyzed")
    first_solve_date: datetime = Field(..., description="Date of first problem solved")
    latest_solve_date: datetime = Field(..., description="Date of most recent problem solved")
    last_updated: datetime = Field(..., description="Timestamp when data was last fetched")
