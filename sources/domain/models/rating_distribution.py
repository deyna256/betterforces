"""Rating distribution domain models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from sources.domain.models.base import BaseDomainModel


@dataclass
class RatingPoint(BaseDomainModel):
    """A single data point in the rating distribution."""

    timestamp: int
    rating: int
    problem_name: str

    @property
    def date(self) -> datetime:
        """Convert timestamp to datetime object."""
        return datetime.fromtimestamp(self.timestamp)


@dataclass
class RatingDistribution(BaseDomainModel):
    """Rating distribution over time for a user."""

    handle: str
    rating_points: List[RatingPoint]
    max_rating_achieved: int
    total_solved: int
    rating_growth_periods: List[str] = field(default_factory=list)

    def get_rating_points_sorted_by_time(self) -> List[RatingPoint]:
        """Get rating points sorted by timestamp."""
        return sorted(self.rating_points, key=lambda x: x.timestamp)
