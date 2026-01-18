"""API dependencies."""

from typing import Any, Dict

from litestar import Request
from litestar.di import Provide

from sources.services.sync_service import SyncService


def get_sync_service() -> SyncService:
    """Dependency provider for SyncService."""
    return SyncService()


def get_request_metadata(request: Request) -> Dict[str, Any]:
    """Extract metadata from the request."""
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip": request.client.host if request.client else None,
    }


# Dependency providers for route handlers
sync_service_dependency = Provide(get_sync_service)
request_metadata_dependency = Provide(get_request_metadata)