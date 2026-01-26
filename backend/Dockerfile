# Use uv image for building
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Do not install development dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a container
ENV UV_LINK_MODE=copy

WORKDIR /app


# Install dependencies separately to leverage cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY . ./backend/
COPY pyproject.toml uv.lock ./

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Final stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /.venv

# Environment variables
ENV PATH="/.venv/bin:$PATH" \
    VIRTUAL_ENV="/.venv" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_NO_DEV=1

WORKDIR /app

# Copy application code
COPY . ./backend/

EXPOSE 8000

# Run the application
CMD ["python", "-m", "backend.main"]
