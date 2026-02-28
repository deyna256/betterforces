"""Division problems domain models."""

from dataclasses import dataclass
from typing import List

from backend.domain.models.base import BaseDomainModel


@dataclass
class DivisionStats(BaseDomainModel):
    """Statistics for a single division."""

    division: str
    contest_count: int
    total_problems_solved: int
    average_problems_per_contest: float


@dataclass
class DivisionProblemsAnalysis(BaseDomainModel):
    """Analysis of average problems solved per division."""

    handle: str
    divisions: List[DivisionStats]
    total_contests: int
    total_problems_solved: int
