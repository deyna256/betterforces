# List all available commands
default:
    @just --list

# Copy example env files to their actual locations (run once on first setup)
init:
    cp -n envs/.env.backend.example envs/.env.backend
    cp -n envs/.env.worker.example envs/.env.worker
    cp -n envs/.env.caddy.example envs/.env.caddy

# Build images for development
build:
    docker compose build

# Start services for development
up:
    docker compose up -d

# Build images for production
build-prod:
    docker compose -f docker-compose.yml --profile prod build

# Start services for production
up-prod:
    docker compose -f docker-compose.yml --profile prod up -d

# Stop all services
down:
    docker compose --profile prod down

# Restart services (dev)
restart:
    just down
    just up

# Restart services (production)
restart-prod:
    just down
    just up-prod

# Show last 250 lines of logs
logs:
    docker compose logs --tail=250

# Stop services and remove volumes/images
clean:
    docker compose --profile prod down -v --rmi local
