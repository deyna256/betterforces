# List all available commands
default:
    @just --list

# Build images for development
build:
    docker compose build

# Start services for development
up:
    docker compose up -d

# Build images for production
build-prod:
    docker compose -f docker-compose.yml build

# Start services for production
up-prod:
    docker compose -f docker-compose.yml up -d

# Stop all services
down:
    docker compose down

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
    docker compose down -v --rmi local
