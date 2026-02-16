"""API schemas package."""

from .base import BaseAPISchema
from .tags import SimpleTagInfoSchema, TagInfoSchema, TagsResponse, WeakTagsResponse

__all__ = [
    "BaseAPISchema",
    "TagsResponse",
    "SimpleTagInfoSchema",
    "TagInfoSchema",
    "WeakTagsResponse",
]
