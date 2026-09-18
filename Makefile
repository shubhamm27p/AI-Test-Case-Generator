.PHONY: help install install-dev test coverage lint format clean build docs demo

help:
	@echo "AI Test Generator - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install package"
	@echo "  make install-dev      Install package with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test            Run tests"
	@echo "  make coverage        Run tests with coverage report"
	@echo "  make lint            Run linters (flake8, mypy)"
	@echo "  make format          Format code with black and isort"
	@echo "  make demo            Run demo script"
	@echo ""
	@echo "Build:"
	@echo "  make build           Build package"
	@echo "  make clean           Clean build artifacts"
	@echo "  make docs            Build documentation"
	@echo ""
	@echo "Quality:"
	@echo "  make quality         Run all quality checks"

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v

coverage:
	pytest tests/ -v --cov=ai_test_generator --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports

format:
	@echo "Formatting with black..."
	black src/ tests/
	@echo "Sorting imports with isort..."
	isort src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	@echo "Documentation generation not yet implemented"
	@echo "See README.md for now"

demo:
	python demo.py

quality: format lint test
	@echo ""
	@echo "✓ All quality checks passed!"

# Development helpers
watch-test:
	pytest-watch tests/

example:
	ai-test-gen analyze examples/calculator.py --output examples/generated_tests/

.DEFAULT_GOAL := help
