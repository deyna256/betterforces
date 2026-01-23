"""API schemas package."""

from .base import BaseAPISchema
from .common import APIResponse, ErrorResponse
from .tags import SimpleTagInfoSchema, TagInfoSchema, TagsResponse, WeakTagsResponse

__all__ = [
    "BaseAPISchema",
    "TagsResponse",
    "SimpleTagInfoSchema",
    "TagInfoSchema",
    "WeakTagsResponse",
    "APIResponse",
    "ErrorResponse",
]
