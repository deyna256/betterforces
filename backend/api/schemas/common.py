"""Common API response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Base API response with metadata."""

    handle: str
    last_updated: datetime
    cache_status: str  # "fresh", "cached", "error"

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: Optional[str] = None
    code: Optional[str] = None
