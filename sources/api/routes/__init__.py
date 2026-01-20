"""API routes package."""

from sources.api.routes.base import BaseMetricController
from sources.api.routes.difficulty_progression import DifficultyProgressionController
from sources.api.routes.rating_distribution import RatingDistributionController
from sources.api.routes.tags import TagsController

routes = [
    DifficultyProgressionController,
    RatingDistributionController,
    TagsController,
]

__all__ = [
    "BaseMetricController",
    "DifficultyProgressionController",
    "RatingDistributionController",
    "TagsController",
    "routes",
]
