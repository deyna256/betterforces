"""API schemas package."""

from .base import BaseAPISchema
from .common import APIResponse, ErrorResponse
from .difficulty_progression import (
    DifficultyPointSchema,
    DifficultyProgressionResponse,
    GrowthRateSchema,
)
from .rating_distribution import RatingDistributionResponse, RatingPointSchema
from .tags import SimpleTagInfoSchema, TagInfoSchema, TagsResponse, WeakTagsResponse

__all__ = [
    "BaseAPISchema",
    "DifficultyProgressionResponse",
    "DifficultyPointSchema",
    "GrowthRateSchema",
    "RatingDistributionResponse",
    "RatingPointSchema",
    "TagsResponse",
    "SimpleTagInfoSchema",
    "TagInfoSchema",
    "WeakTagsResponse",
    "APIResponse",
    "ErrorResponse",
]
