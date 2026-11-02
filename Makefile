.PHONY: help venv install install-dev test lint format db-up db-down db-logs psql clean

PY ?= python3.11

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

venv: ## Create the virtual environment
	$(PY) -m venv .venv && echo "Run: source .venv/bin/activate"

install: ## Install runtime dependencies
	pip install -e .

install-dev: ## Install dev dependencies
	pip install -e ".[dev]"

test: ## Run the test suite
	pytest

lint: ## Lint
	ruff check src tests

format: ## Format
	ruff format src tests

db-up: ## Start PostGIS + Adminer
	docker compose up -d db adminer

db-down: ## Stop the stack
	docker compose down

db-logs: ## Tail database logs
	docker compose logs -f db

psql: ## Open a psql shell
	docker compose exec db psql -U $${POSTGRES_USER:-bri} -d $${POSTGRES_DB:-bri}

clean: ## Remove caches
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
