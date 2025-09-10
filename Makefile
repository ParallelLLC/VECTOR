# Makefile for Vector - Issue-Conditioned Discovery & Ranking System
# Parallel LLC

.PHONY: help install install-dev test lint format clean build run-pipeline run-service docs venv

# Default target
help:
	@echo "Vector - Issue-Conditioned Discovery & Ranking System"
	@echo "=================================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run test suite"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts and cache"
	@echo "  build        Build package"
	@echo "  run-pipeline Run the Vector pipeline with example data"
	@echo "  run-service  Start the FastAPI web service"
	@echo "  docs         Generate documentation"
	@echo ""

# Virtual environment
venv:
	python -m venv .venv && . .venv/bin/activate && pip install -e .

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	python -m pytest tests/ -v --cov=src/vector --cov-report=html --cov-report=term

test-unit:
	python -m pytest tests/unit/ -v

test-integration:
	python -m pytest tests/integration/ -v

# Code quality
lint:
	flake8 src/ tests/
	mypy src/vector/

format:
	black src/ tests/
	isort src/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Build
build: clean
	python -m build

# Development
run-pipeline:
	python -m vector.cli run-pipeline \
		--users data/external/users.csv \
		--edges data/external/edges.csv \
		--posts data/external/posts.csv \
		--taxonomy data/external/taxonomy.yaml \
		--out outputs/

run-service:
	uvicorn vector.service:app --reload --host 0.0.0.0 --port 8000

# Data processing examples
example-gdelt:
	python docs/examples/gdelt_example.py

example-reddit:
	python docs/examples/reddit_example.py

# Documentation
docs:
	@echo "Documentation available in docs/"
	@echo "- Project Structure: docs/PROJECT_STRUCTURE.md"
	@echo "- GDELT Usage: docs/guides/GDELT_USAGE.md"
	@echo "- Reddit Usage: docs/guides/REDDIT_USAGE.md"
	@echo "- Reddit Setup: docs/guides/REDDIT_SETUP.md"

# Docker
docker-build:
	docker build -t vector:latest .

docker-run:
	docker run -p 8000:8000 vector:latest

# Legacy aliases
api: run-service
docker: docker-build docker-run
