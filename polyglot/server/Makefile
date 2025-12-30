# Development commands for polyglot/server

# Default ports
MJS_PORT ?= 53000
PY_PORT ?= 54000

# Get the directory where Makefile is located
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Use local .venv if it exists, otherwise use system Python
VENV_DIR := $(MAKEFILE_DIR)py/.venv
PYTHON := $(if $(wildcard $(VENV_DIR)/bin/python),$(VENV_DIR)/bin/python,python)

.PHONY: help install install-mjs install-py dev dev-mjs dev-py clean clean-ports \
	test test-mjs test-py test-fastify test-fastapi test-coverage \
	examples examples-py examples-mjs example-fastapi example-fastify

help:
	@echo "Polyglot Server Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies (npm + poetry)"
	@echo "  make install-mjs   - Install Node.js dependencies"
	@echo "  make install-py    - Install Python dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run both servers in parallel"
	@echo "  make dev-mjs       - Run Node.js server only (port $(MJS_PORT))"
	@echo "  make dev-py        - Run Python server only (port $(PY_PORT))"
	@echo "  make clean-ports   - Kill processes on dev ports ($(MJS_PORT), $(PY_PORT))"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests (Python + Node.js)"
	@echo "  make test-py       - Run Python tests only"
	@echo "  make test-mjs      - Run Node.js tests only"
	@echo "  make test-fastapi  - Run FastAPI integration tests"
	@echo "  make test-fastify  - Run Fastify integration tests"
	@echo "  make test-coverage - Run tests with coverage"
	@echo ""
	@echo "Examples:"
	@echo "  make examples        - Run all basic usage examples"
	@echo "  make examples-py     - Run Python basic usage examples"
	@echo "  make examples-mjs    - Run Node.js basic usage examples"
	@echo "  make example-fastapi - Run FastAPI example server"
	@echo "  make example-fastify - Run Fastify example server"
	@echo ""
	@echo "Clean:"
	@echo "  make clean         - Clean build artifacts"

# Install all dependencies
install: install-mjs install-py

install-mjs:
	cd $(MAKEFILE_DIR)mjs && npm install

install-py:
	cd $(MAKEFILE_DIR)py && poetry install --no-root

# Clean development ports before starting
clean-ports:
	@echo "Cleaning ports $(MJS_PORT) and $(PY_PORT)..."
	@lsof -ti:$(MJS_PORT) | xargs kill -9 2>/dev/null || true
	@lsof -ti:$(PY_PORT) | xargs kill -9 2>/dev/null || true

# Development - run both servers in parallel
dev: clean-ports
	@echo "Starting development servers..."
	@echo "  Node.js (mjs):  http://localhost:$(MJS_PORT)"
	@echo "  Python (py):    http://localhost:$(PY_PORT)"
	@echo ""
	@$(MAKE) dev-mjs & $(MAKE) dev-py & wait

# Run Node.js server
dev-mjs:
	cd $(MAKEFILE_DIR)mjs && PORT=$(MJS_PORT) node src/main.mjs

# Run Python server
dev-py:
	cd $(MAKEFILE_DIR)py && PORT=$(PY_PORT) $(PYTHON) app/main.py

# Clean build artifacts
clean:
	find $(MAKEFILE_DIR) -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find $(MAKEFILE_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(MAKEFILE_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find $(MAKEFILE_DIR) -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find $(MAKEFILE_DIR) -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# Testing
# ============================================================================

# Run all tests
test: test-py test-mjs

# Run Python unit tests
test-py:
	@echo "Running Python server tests..."
	cd $(MAKEFILE_DIR)py && \
		PYTHONPATH=app:$(PYTHONPATH) \
		$(PYTHON) -m pytest __tests__/ -v --tb=short

# Run Node.js unit tests
test-mjs:
	@echo "Running Node.js server tests..."
	cd $(MAKEFILE_DIR)mjs && \
		NODE_OPTIONS="--experimental-vm-modules" npx jest --passWithNoTests

# Run FastAPI integration tests only
test-fastapi:
	@echo "Running FastAPI integration tests..."
	cd $(MAKEFILE_DIR)py && \
		PYTHONPATH=app:$(PYTHONPATH) \
		$(PYTHON) -m pytest __tests__/test_api.py -v --tb=short

# Run Fastify integration tests only
test-fastify:
	@echo "Running Fastify integration tests..."
	cd $(MAKEFILE_DIR)mjs && \
		NODE_OPTIONS="--experimental-vm-modules" npx jest __tests__/api.test.mjs --passWithNoTests

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	cd $(MAKEFILE_DIR)py && \
		PYTHONPATH=app:$(PYTHONPATH) \
		$(PYTHON) -m pytest __tests__/ -v --cov=app --cov-report=html
	cd $(MAKEFILE_DIR)mjs && \
		NODE_OPTIONS="--experimental-vm-modules" npx jest --coverage

# ============================================================================
# Examples
# ============================================================================

# Run all basic usage examples
examples: examples-py examples-mjs

# Run Python basic usage examples
examples-py:
	@echo "Running Python basic usage examples..."
	cd $(MAKEFILE_DIR)py/examples && \
		PYTHONPATH=$(MAKEFILE_DIR)py/app:$(PYTHONPATH) \
		$(PYTHON) basic_usage.py

# Run Node.js basic usage examples
examples-mjs:
	@echo "Running Node.js basic usage examples..."
	cd $(MAKEFILE_DIR)mjs/examples && \
		LOG_LEVEL=debug node basic-usage.mjs

# Run FastAPI example server (development mode)
example-fastapi:
	@echo "Starting FastAPI example server on port $(PY_PORT)..."
	cd $(MAKEFILE_DIR)py/examples && \
		PYTHONPATH=$(MAKEFILE_DIR)py/app:$(PYTHONPATH) \
		PORT=$(PY_PORT) \
		$(PYTHON) -m uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port $(PY_PORT)

# Run Fastify example server (development mode)
example-fastify:
	@echo "Starting Fastify example server on port $(MJS_PORT)..."
	cd $(MAKEFILE_DIR)mjs/examples && \
		PORT=$(MJS_PORT) LOG_LEVEL=debug node fastify-app/server.mjs
