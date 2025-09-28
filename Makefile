.PHONY: help install-dev setup-hooks test lint format clean

help: ## Show this help message
	@echo "Research Agent Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

setup-hooks: ## Install pre-commit hooks
	pre-commit install

setup: install-dev setup-hooks ## Complete development setup
	@echo "✅ Development environment ready!"

test: ## Run tests
	python -m pytest tests/ -v --cov=research_agent

lint: ## Run all linting checks
	pre-commit run --all-files

format: ## Format code with black and isort
	black research_agent/ examples/ tests/
	isort research_agent/ examples/ tests/

check-types: ## Run type checking with mypy
	mypy research_agent/ --ignore-missing-imports

check-security: ## Run security checks with bandit
	bandit -r research_agent/ -f json

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

quick-test: ## Quick test of research agent functionality
	python examples/phase2_example.py

ci: lint test ## Run CI pipeline (lint + test)

all: clean setup ci ## Run complete development pipeline
