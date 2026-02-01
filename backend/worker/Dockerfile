FROM python:3.13-slim

WORKDIR /app

# Copy pyproject.toml from parent backend directory
COPY pyproject.toml ./

# Install uv and dependencies
RUN pip install uv && uv pip install --system .

# Copy entire backend directory
COPY . .

CMD ["python", "-m", "backend.worker.main"]
