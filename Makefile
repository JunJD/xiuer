.PHONY: help

# ==============================================================================
# VARIABLES
# ==============================================================================

DOCKER_COMPOSE := docker compose
PROD_COMPOSE_FILES := -f docker-compose.yml -f docker-compose.prod.yml

# ==============================================================================
# COMMANDS
# ==============================================================================

help: ## Show this help message.
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z\._-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sed 's/://'

# --- Local Development ---
up: ## Start local services in the background. Uses docker-compose.override.yml.
	$(DOCKER_COMPOSE) up --build -d

down: ## Stop local services.
	$(DOCKER_COMPOSE) down

logs: ## Follow logs for local services.
	$(DOCKER_COMPOSE) logs -f

shell: ## Access the backend container shell (local).
	$(DOCKER_COMPOSE) exec backend sh

# --- Production Deployment (to be run on server) ---
deploy: ## Deploy the application stack for production.
	$(DOCKER_COMPOSE) $(PROD_COMPOSE_FILES) pull
	$(DOCKER_COMPOSE) $(PROD_COMPOSE_FILES) up --build -d
	@echo "Waiting for backend to be ready for migration..."
	@sleep 10
	make migrate-prod

migrate: ## Run database migrations (local).
	$(DOCKER_COMPOSE) exec backend alembic upgrade head

migrate-prod: ## Run database migrations (production).
	$(DOCKER_COMPOSE) $(PROD_COMPOSE_FILES) exec backend alembic upgrade head

makemigrations: ## Create a new database migration. Usage: make makemigrations name="my migration"
	$(DOCKER_COMPOSE) exec backend alembic revision --autogenerate -m "$(name)"

test-backend: ## Run tests for the backend (local).
	$(DOCKER_COMPOSE) exec backend pytest

test-frontend: ## Run tests for the frontend (local).
	$(DOCKER_COMPOSE) exec frontend pnpm test