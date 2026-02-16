"""Daily activity domain models."""

from dataclasses import dataclass
from typing import List

from backend.domain.models.base import BaseDomainModel


@dataclass
class DailyActivity(BaseDomainModel):
    """Activity stats for a single time bucket (minute, hour, day, month, or year)."""

    date: str
    solved_count: int
    attempt_count: int


@dataclass
class DailyActivityAnalysis(BaseDomainModel):
    """Aggregated activity analysis over a time range."""

    handle: str
    days: List[DailyActivity]
    total_solved: int
    total_attempts: int
    active_days: int
