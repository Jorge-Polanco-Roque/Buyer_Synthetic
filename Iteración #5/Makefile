.PHONY: help install install-dev test test-cov lint format type-check security-check clean build docker-build docker-run docker-test pre-commit setup-vault

# Colors for help
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Buyer Synthetic™ Development Commands$(RESET)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install all dependencies including dev
	poetry install

# Testing
test: ## Run tests
	poetry run pytest tests/ -v

test-cov: ## Run tests with coverage
	poetry run pytest tests/ -v --cov=src/buyer_synthetic --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/python tests/test_langgraph_integration.py

# Code Quality
lint: ## Run all linters
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

format: ## Format code
	poetry run black src/ tests/
	poetry run isort src/ tests/
	poetry run ruff check --fix src/ tests/

type-check: ## Run type checking
	poetry run mypy src/

security-check: ## Run security checks
	poetry run bandit -r src/
	poetry run safety check

# Pre-commit
pre-commit: ## Run pre-commit hooks
	poetry run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	poetry run pre-commit install

# Build
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

build: clean ## Build package
	poetry build

# Docker
docker-build: ## Build Docker image
	docker build -t buyer-synthetic:latest .

docker-run: ## Run Docker container
	docker run -p 8505:8505 --env-file .env buyer-synthetic:latest

docker-test: ## Run tests in Docker
	docker run --rm --env OPENAI_API_KEY=test-key buyer-synthetic:latest python -m pytest tests/ -v

docker-compose-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop all services
	docker-compose down

docker-compose-vault: ## Start services including Vault
	docker-compose --profile vault up -d

# Development Server
dev: ## Run development server (complete application)
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/streamlit run src/buyer_synthetic/ui/dashboard.py --server.port 8505

dev-simple: ## Run simple development server (basic version)
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/streamlit run src/buyer_synthetic/ui/dashboard_simple.py --server.port 8505

dev-watch: ## Run development server with auto-reload
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/streamlit run src/buyer_synthetic/ui/dashboard.py --server.port 8505 --server.runOnSave true

audit-dashboard: ## Run audit dashboard for trace analysis
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/streamlit run src/buyer_synthetic/ui/audit_dashboard.py --server.port 8506

audit-chat: ## Test audit chatbot in CLI
	export PYTHONPATH="$(shell pwd)/src" && ./.venv/bin/python -c "from src.buyer_synthetic.agents.audit_chatbot import create_audit_chatbot; bot = create_audit_chatbot(); print(bot.chat('¿Qué procesos se ejecutaron hoy?'))"

# Vault Management
setup-vault: ## Initialize and setup Vault
	./scripts/vault-init.sh

vault-unseal: ## Unseal Vault
	@echo "$(YELLOW)Unsealing Vault...$(RESET)"
	vault operator unseal

vault-status: ## Check Vault status
	vault status

# Project Management
deps-update: ## Update dependencies
	poetry update

deps-audit: ## Audit dependencies for security issues
	poetry run safety check

# Utility
check-all: lint type-check security-check test ## Run all checks
	@echo "$(GREEN)✅ All checks passed!$(RESET)"

ci-local: ## Simulate CI pipeline locally
	@echo "$(BLUE)🚀 Running local CI simulation...$(RESET)"
	make clean
	make install-dev
	make check-all
	make build
	make docker-build
	@echo "$(GREEN)🎉 CI simulation completed successfully!$(RESET)"

# Environment setup
setup: ## Complete project setup
	@echo "$(BLUE)🔧 Setting up Buyer Synthetic™ development environment...$(RESET)"
	poetry install
	poetry run pre-commit install
	@echo "$(GREEN)✅ Setup completed! Run 'make help' to see available commands.$(RESET)"

# Health checks
health-check: ## Check application health
	curl -f http://localhost:8505/_stcore/health || echo "$(RED)Health check failed$(RESET)"

# Environment Management
env-init: ## Initialize environment file (usage: make env-init ENV=dev)
	./scripts/env-utils.sh init $(ENV)

env-check: ## Check current environment configuration
	./scripts/env-utils.sh check

env-validate: ## Validate environment file (usage: make env-validate ENV=prod)
	./scripts/env-utils.sh validate $(ENV)

env-switch: ## Switch environment (usage: make env-switch ENV=staging)
	./scripts/env-utils.sh switch $(ENV)

env-backup: ## Backup environment files
	./scripts/env-utils.sh backup

generate-key: ## Generate secure random key
	./scripts/env-utils.sh generate-key

# Logs
logs: ## Show application logs
	tail -f logs/buyer_synthetic_$(shell date +%Y%m%d).log


# Default target
.DEFAULT_GOAL := help