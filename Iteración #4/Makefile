# Buyer Synthetic Development Makefile

.PHONY: help install dev test lint format clean build docs deploy

# Default target
help:
	@echo "Buyer Synthetic™ Development Commands"
	@echo "===================================="
	@echo
	@echo "Setup Commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Install development dependencies"
	@echo "  clean       Clean build artifacts"
	@echo
	@echo "Development Commands:"
	@echo "  format      Format code with black and isort"
	@echo "  lint        Lint code with flake8, mypy, and ruff"
	@echo "  test        Run tests with pytest"
	@echo "  test-cov    Run tests with coverage"
	@echo "  test-fast   Run tests excluding slow ones"
	@echo
	@echo "Application Commands:"
	@echo "  dashboard   Start Streamlit dashboard"
	@echo "  cli         Show CLI help"
	@echo "  sample      Create sample data"
	@echo
	@echo "Build Commands:"
	@echo "  build       Build package"
	@echo "  docs        Build documentation"
	@echo "  docker      Build Docker image"
	@echo
	@echo "Deployment Commands:"
	@echo "  deploy-dev  Deploy to development"
	@echo "  deploy-prod Deploy to production"

# Setup
install:
	pip install -e .

dev:
	pip install -e ".[dev,test,docs]"
	pre-commit install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Development
format:
	black src/ tests/
	isort src/ tests/

lint:
	flake8 src/ tests/
	mypy src/
	ruff check src/ tests/

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=buyer_synthetic --cov-report=html --cov-report=term

test-fast:
	pytest tests/ -v -m "not slow"

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Application
dashboard:
	streamlit run src/buyer_synthetic/ui/dashboard.py

cli:
	python -m buyer_synthetic.cli --help

sample:
	python -m buyer_synthetic.cli create-sample --size 100

# Build
build:
	python -m build

docs:
	mkdocs build

docker:
	docker build -t buyer-synthetic:latest .

# Quality checks
check: lint test

pre-commit:
	pre-commit run --all-files

# Data management
clean-data:
	rm -rf data/output/*
	rm -rf data/temp/*
	rm -rf logs/*

backup-data:
	tar -czf data_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/

# Development utilities
jupyter:
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

profile:
	python -m cProfile -o profile.stats -m buyer_synthetic.cli analyze examples/sample_results.csv

benchmark:
	python -m pytest tests/ --benchmark-only

# Deployment (examples)
deploy-dev:
	@echo "Deploying to development environment..."
	# Add your deployment commands here

deploy-prod:
	@echo "Deploying to production environment..."
	# Add your deployment commands here

# Environment setup
env-dev:
	cp .env.example .env.dev
	@echo "Development environment file created. Please edit .env.dev"

env-prod:
	cp .env.example .env.prod
	@echo "Production environment file created. Please edit .env.prod"

# Docker development
docker-dev:
	docker-compose -f docker-compose.dev.yml up -d

docker-prod:
	docker-compose -f docker-compose.prod.yml up -d

# Package management
requirements:
	pip-compile pyproject.toml --output-file requirements.txt
	pip-compile pyproject.toml --extra dev --output-file requirements-dev.txt

upgrade:
	pip-compile --upgrade pyproject.toml --output-file requirements.txt
	pip-compile --upgrade pyproject.toml --extra dev --output-file requirements-dev.txt