"""Tags domain models."""

from dataclasses import dataclass
from typing import List

from sources.domain.models.base import BaseDomainModel


@dataclass
class TagInfo(BaseDomainModel):
    """Information about a single tag."""

    tag: str
    average_rating: float
    problem_count: int
    problems: List[str]


@dataclass
class TagsAnalysis(BaseDomainModel):
    """Analysis of user's problem-solving activity by tags."""

    handle: str
    tags: List[TagInfo]
    overall_average_rating: float
    total_solved: int

    def get_weak_tags(self, threshold_diff: int = 200) -> List[TagInfo]:
        """
        Get tags where average rating is significantly lower than overall average.

        Args:
            threshold_diff: Minimum rating difference to consider a tag "weak"

        Returns:
            List of tags with average rating significantly below overall average
        """
        if not self.tags or self.total_solved == 0:
            return []

        weak_tags = []
        for tag_info in self.tags:
            if self.overall_average_rating - tag_info.average_rating >= threshold_diff:
                weak_tags.append(tag_info)

        # Sort by how much lower the average is
        weak_tags.sort(key=lambda x: self.overall_average_rating - x.average_rating, reverse=True)
        return weak_tags
