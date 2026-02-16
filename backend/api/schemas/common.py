"""Common API response schemas."""

from pydantic import BaseModel


class AsyncTaskResponse(BaseModel):
    """Response schema for async task processing (202 Accepted)."""

    status: str  # "processing"
    task_id: str
    retry_after: int  # Seconds to wait before retrying
