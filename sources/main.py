#!/usr/bin/env python3
"""Entry point for the BetterForces application."""

import os
import uvicorn
from sources.api.app import create_app


def main() -> None:
    """Run the application."""
    from sources.config import settings
    # Enable reload in development mode
    reload_mode = settings.dev_mode

    if reload_mode:
        # For development with reload, use import string
        uvicorn.run(
            "sources.api.app:create_app",
            host="0.0.0.0",  # Listen on all interfaces for Docker
            port=8000,
            reload=True,
            reload_dirs=["/app/sources"],
            factory=True,
        )
    else:
        # For production, use the app object
        app = create_app()
        uvicorn.run(
            app,
            host="0.0.0.0",  # Listen on all interfaces for Docker
            port=8000,
        )


if __name__ == "__main__":
    main()