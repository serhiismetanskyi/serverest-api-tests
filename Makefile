.PHONY: help install test test-html lint format format-check fix clean all \
	docker-build docker-test docker-test-html docker-shell docker-clean

help:
	@echo "Available commands:"
	@echo ""
	@echo "Local:"
	@echo "  make install        - Install dependencies with uv (including dev tools)"
	@echo "  make test           - Run test suite"
	@echo "  make test-html      - Run tests and generate HTML report"
	@echo "  make lint           - Run Ruff lint checks"
	@echo "  make format         - Format code with Ruff"
	@echo "  make format-check   - Check formatting without modifying files"
	@echo "  make fix            - Auto-fix lint issues and format code"
	@echo "  make clean          - Remove cache artifacts, reports, and logs"
	@echo "  make all            - Install, format, lint, and test (full workflow)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker image"
	@echo "  make docker-test       - Run tests in Docker (headless)"
	@echo "  make docker-test-html  - Run tests in Docker with HTML report"
	@echo "  make docker-shell      - Open shell in Docker container"
	@echo "  make docker-clean      - Remove Docker containers and images"

install:
	uv sync

test:
	mkdir -p logs
	uv run python -m pytest

test-html:
	mkdir -p logs
	mkdir -p reports
	rm -rf reports/* 2>/dev/null || true
	uv run python -m pytest --html=reports/test_report.html --self-contained-html

lint:
	uv run ruff check config.py services/ tests/ utils/

format:
	uv run ruff format config.py services/ tests/ utils/

format-check:
	uv run ruff format --check config.py services/ tests/ utils/

fix:
	uv run ruff check --fix config.py services/ tests/ utils/
	uv run ruff format config.py services/ tests/ utils/

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf .vscode
	rm -rf reports
	rm -rf logs
	@echo "Cleanup complete!"

all: install format lint test

docker-build:
	mkdir -p logs
	docker compose build

docker-test:
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests

docker-test-html:
	mkdir -p logs
	mkdir -p reports
	rm -rf reports/* 2>/dev/null || true
	docker compose run --rm -v $(CURDIR)/logs:/app/logs -v $(CURDIR)/reports:/app/reports tests uv run python -m pytest tests --html=./reports/test_report.html --self-contained-html

docker-shell:
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests /bin/bash

docker-clean:
	docker compose down --rmi local --volumes --remove-orphans || true
