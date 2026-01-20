"""Difficulty progression domain models."""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from sources.domain.models.base import BaseDomainModel


@dataclass
class DifficultyPoint(BaseDomainModel):
    """A data point showing average difficulty at a specific time period."""

    date_month: str
    date_quarter: str
    average_rating: float
    problem_count: int
    period_start: datetime
    period_end: datetime


@dataclass
class GrowthRate(BaseDomainModel):
    """Growth rate calculation between two periods."""

    from_period: str
    to_period: str
    rating_change: float
    monthly_growth: float
    months_difference: int


@dataclass
class DifficultyProgression(BaseDomainModel):
    """Analysis of user's difficulty progression over time."""

    handle: str
    monthly_progression: List[DifficultyPoint]
    quarterly_progression: List[DifficultyPoint]
    growth_rates: List[GrowthRate]
    total_solved: int
    periods_analyzed: int
    first_solve_date: datetime
    latest_solve_date: datetime
