.PHONY: help setup dev test lint seed demo up down logs clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup: copy env, bootstrap, bring up stack
	@test -f .env || cp .env.example .env
	@bash scripts/bootstrap.sh

up: ## Start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## Tail logs
	docker compose logs -f

dev-api: ## Run API locally (no Docker)
	cd api && uvicorn app.main:app --reload --port 8000

dev-web: ## Run frontend locally (no Docker)
	cd web && npm run dev

seed: ## Seed demo data
	docker compose exec api python -m scripts.seed_demo_data

test: ## Run backend tests with coverage
	cd api && python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-fail-under=80

test-ci: ## Run tests in CI mode
	cd api && python -m pytest tests/ -v --tb=short --cov=app --cov-report=xml --cov-fail-under=80

lint: ## Lint backend
	cd api && python -m ruff check app/ tests/

demo: setup ## Full demo: setup + seed + open browser
	@echo "\n🚀 TalentPulse is running!"
	@echo "   Dashboard: http://localhost:3000"
	@echo "   API docs:  http://localhost:8000/docs"
	@echo "   Health:    http://localhost:8000/health"

clean: ## Remove all containers, volumes, and generated files
	docker compose down -v --remove-orphans
	rm -rf api/__pycache__ api/.pytest_cache web/.next web/node_modules
