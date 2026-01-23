"""Difficulty distribution domain models."""

from dataclasses import dataclass
from typing import List

from backend.domain.models.base import BaseDomainModel


@dataclass
class RatingRange(BaseDomainModel):
    """A rating range grouping problems by difficulty."""

    rating: int
    problem_count: int


@dataclass
class DifficultyDistribution(BaseDomainModel):
    """Distribution of solved problems by difficulty levels."""

    handle: str
    ranges: List[RatingRange]
    total_solved: int
