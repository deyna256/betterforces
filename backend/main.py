#!/usr/bin/env python3
"""Entry point for the BetterForces application."""

import os
import sys
import uvicorn

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.app import create_app


def main() -> None:
    """Run the application."""
    from backend.config import settings

    # Enable reload in development mode
    reload_mode = settings.dev_mode

    if reload_mode:
        # For development with reload, use import string
        uvicorn.run(
            "backend.api.app:create_app",
            host="0.0.0.0",  # Listen on all interfaces for Docker
            port=8000,
            reload=True,
            reload_dirs=["/app/backend"],
            factory=True,
            log_level="info",
            access_log=True,
        )
    else:
        # For production, use the app object
        app = create_app()
        uvicorn.run(
            app,
            host="0.0.0.0",  # Listen on all interfaces for Docker
            port=8000,
            log_level="info",
            access_log=True,
        )


if __name__ == "__main__":
    main()
