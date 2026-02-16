"""Daily activity domain models."""

from dataclasses import dataclass
from typing import List

from backend.domain.models.base import BaseDomainModel


@dataclass
class DailyActivity(BaseDomainModel):
    """Activity stats for a single day."""

    date: str  # "2025-01-15"
    solved_count: int  # unique accepted problems
    attempt_count: int  # all other submissions


@dataclass
class DailyActivityAnalysis(BaseDomainModel):
    """Daily activity analysis result."""

    handle: str
    days: List[DailyActivity]
    total_solved: int
    total_attempts: int
    active_days: int  # days with solved_count > 0 or attempt_count > 0
