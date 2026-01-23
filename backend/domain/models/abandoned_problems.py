"""Abandoned problems domain models."""

from dataclasses import dataclass
from typing import List

from backend.domain.models.base import BaseDomainModel


@dataclass
class AbandonedProblem(BaseDomainModel):
    """A problem that was attempted but never solved."""

    contest_id: int
    index: str
    name: str
    rating: int
    tags: List[str]
    failed_attempts: int


@dataclass
class TagAbandonedStats(BaseDomainModel):
    """Abandoned problems statistics by tag."""

    tag: str
    problem_count: int
    total_failed_attempts: int


@dataclass
class RatingAbandonedStats(BaseDomainModel):
    """Abandoned problems statistics by rating."""

    rating: int
    problem_count: int
    total_failed_attempts: int


@dataclass
class AbandonedProblemsAnalysis(BaseDomainModel):
    """Complete analysis of user's abandoned problems."""

    handle: str
    abandoned_problems: List[AbandonedProblem]
    total_abandoned: int
    tags_stats: List[TagAbandonedStats]
    ratings_stats: List[RatingAbandonedStats]
