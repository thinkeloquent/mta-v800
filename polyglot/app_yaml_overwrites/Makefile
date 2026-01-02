# =============================================================================
# app_yaml_overwrites - Unified Configuration SDK (Polyglot)
# =============================================================================

.PHONY: install clean test test-py test-mjs test-all build lint

# Default target
all: install

# =============================================================================
# Installation
# =============================================================================

install:
	@echo "Installing polyglot packages..."
	cd mjs && npm install
	cd py && pip install -e ".[dev]"

install-dev: install
	@echo "Dev dependencies installed"

# =============================================================================
# Build
# =============================================================================

build:
	@echo "Building packages..."
	cd mjs && npm run build

build-py:
	@echo "Python package is source-only, no build needed"

build-mjs:
	cd mjs && npm run build

# =============================================================================
# Testing
# =============================================================================

# Run all tests (Python + Node.js)
test: test-all

test-all: test-py test-mjs
	@echo ""
	@echo "=============================================="
	@echo "All tests completed"
	@echo "=============================================="

# Python tests with pytest
test-py:
	@echo ""
	@echo "=============================================="
	@echo "Running Python tests (pytest)"
	@echo "=============================================="
	cd py && python -m pytest __tests__/ -v --tb=short

# Python tests with coverage
test-py-cov:
	@echo "Running Python tests with coverage..."
	cd py && python -m pytest __tests__/ -v --cov=src/app_yaml_overwrites --cov-report=html --cov-report=term

# Node.js tests with Vitest
test-mjs:
	@echo ""
	@echo "=============================================="
	@echo "Running Node.js tests (Vitest)"
	@echo "=============================================="
	cd mjs && npm test

# Node.js tests with coverage
test-mjs-cov:
	@echo "Running Node.js tests with coverage..."
	cd mjs && npm run test:coverage

# Watch mode for development
test-watch-py:
	cd py && python -m pytest __tests__/ -v --tb=short -f

test-watch-mjs:
	cd mjs && npm run test:watch

# =============================================================================
# Integration Tests (FastAPI + Fastify)
# =============================================================================

test-fastapi:
	@echo "Running FastAPI integration tests..."
	cd py && python -m pytest __tests__/test_*_integration.py -v --tb=short

test-fastify:
	@echo "Running Fastify integration tests..."
	cd mjs && npm run test -- --grep "Integration"

# =============================================================================
# Linting
# =============================================================================

lint: lint-py lint-mjs

lint-py:
	@echo "Linting Python code..."
	cd py && python -m ruff check src/ __tests__/ || true

lint-mjs:
	@echo "Linting Node.js code..."
	cd mjs && npm run lint 2>/dev/null || true

# =============================================================================
# Clean
# =============================================================================

clean:
	@echo "Cleaning build artifacts..."
	rm -rf mjs/node_modules mjs/dist
	rm -rf py/*.egg-info py/__pycache__ py/src/*.egg-info
	rm -rf py/.pytest_cache py/__tests__/__pycache__
	rm -rf mjs/coverage py/htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# Help
# =============================================================================

help:
	@echo "app_yaml_overwrites - Makefile targets"
	@echo ""
	@echo "Installation:"
	@echo "  install       Install all dependencies"
	@echo "  install-dev   Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests (Python + Node.js)"
	@echo "  test-py       Run Python tests only"
	@echo "  test-mjs      Run Node.js tests only"
	@echo "  test-py-cov   Run Python tests with coverage"
	@echo "  test-mjs-cov  Run Node.js tests with coverage"
	@echo "  test-fastapi  Run FastAPI integration tests"
	@echo "  test-fastify  Run Fastify integration tests"
	@echo ""
	@echo "Build:"
	@echo "  build         Build all packages"
	@echo "  build-mjs     Build Node.js package"
	@echo ""
	@echo "Utilities:"
	@echo "  lint          Run linters"
	@echo "  clean         Remove build artifacts"
	@echo "  help          Show this help"
