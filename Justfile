# List available commands
default:
    @just --list

# Build services
build:
    docker compose build

# Start services
up:
    docker compose up -d

# Stop services
down:
    docker compose down

# Restart services
restart:
    just down
    just up

# View logs
logs:
    docker compose logs --tail=250

# Clean up
clean:
    docker compose down -v --rmi local
    rm -rf .pytest_cache .ruff_cache .venv build dist *.egg-info

# Run tests
test:
    uv run pytest

# Format code
format:
    uv run ruff format .

# Run linting
lint:
    uv run ruff check .

# Run linting with auto-fix
lintfix:
    uv run ruff check --fix .

# Run type checking
typecheck:
    uv run ty check
