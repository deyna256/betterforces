"""Pydantic schemas for API responses.

This module contains base response schemas.
Concrete API response models will be added during development phase.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response schema with metadata."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class UserAnalysisResponse(BaseResponse):
    """Response schema for user analysis."""

    handle: str
    analysis_type: str
    result: Dict[str, Any]


class ProblemResponse(BaseResponse):
    """Response schema for problem data."""

    problem_id: str
    problem_data: Dict[str, Any]


class GeneralAnalysisResponse(BaseResponse):
    """General analysis response."""

    analysis_type: str
    parameters: Dict[str, Any]
    results: Dict[str, Any]
