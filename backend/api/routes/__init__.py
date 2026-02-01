"""API routes package."""

from backend.api.routes.abandoned_problems import AbandonedProblemsController
from backend.api.routes.base import BaseMetricController
from backend.api.routes.difficulty_distribution import DifficultyDistributionController
from backend.api.routes.tags import TagsController
from backend.api.routes.tasks import TaskController

routes = [
    AbandonedProblemsController,
    DifficultyDistributionController,
    TagsController,
    TaskController,
]

__all__ = [
    "AbandonedProblemsController",
    "BaseMetricController",
    "DifficultyDistributionController",
    "TagsController",
    "TaskController",
    "routes",
]
