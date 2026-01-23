from pydantic import BaseModel, ConfigDict


class BaseAPISchema(BaseModel):
    """Base class for all API schemas with automatic dataclass conversion support."""

    model_config = ConfigDict(from_attributes=True)
