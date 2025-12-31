.PHONY: test test-js test-py test-fastify test-fastapi install install-js install-py clean lint format check help

# Directories
JS_DIR := mjs
PY_DIR := py

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo ""
	@echo "  install       - Install all dependencies (JS + Python)"
	@echo "  install-js    - Install JavaScript dependencies"
	@echo "  install-py    - Install Python dependencies"
	@echo ""
	@echo "  test          - Run all tests (JS + Python)"
	@echo "  test-js       - Run all JavaScript tests"
	@echo "  test-py       - Run all Python tests"
	@echo "  test-fastify  - Run Fastify integration tests"
	@echo "  test-fastapi  - Run FastAPI integration tests"
	@echo ""
	@echo "  lint          - Run all linters"
	@echo "  lint-js       - Lint JavaScript"
	@echo "  lint-py       - Lint Python"
	@echo ""
	@echo "  clean         - Clean build artifacts"

# =============================================================================
# Test Targets
# =============================================================================

test: test-js test-py
	@echo ""
	@echo "=============================================="
	@echo "All tests completed successfully!"
	@echo "=============================================="

test-js:
	@echo ""
	@echo "=============================================="
	@echo "Running JavaScript/TypeScript tests..."
	@echo "=============================================="
	cd $(JS_DIR) && npm test

test-py:
	@echo ""
	@echo "=============================================="
	@echo "Running Python tests..."
	@echo "=============================================="
	cd $(PY_DIR) && poetry run pytest -v

# Framework-specific integration tests
test-fastify:
	@echo ""
	@echo "=============================================="
	@echo "Running Fastify integration tests..."
	@echo "=============================================="
	cd $(JS_DIR) && npm test -- --testPathPattern="integrations/fastify"

test-fastapi:
	@echo ""
	@echo "=============================================="
	@echo "Running FastAPI integration tests..."
	@echo "=============================================="
	cd $(PY_DIR) && poetry run pytest tests/test_api.py -v

# =============================================================================
# Install Targets
# =============================================================================

install: install-js install-py
	@echo ""
	@echo "=============================================="
	@echo "All dependencies installed!"
	@echo "=============================================="

install-js:
	@echo ""
	@echo "Installing JavaScript dependencies..."
	cd $(JS_DIR) && npm install

install-py:
	@echo ""
	@echo "Installing Python dependencies..."
	cd $(PY_DIR) && poetry install

# =============================================================================
# Lint Targets
# =============================================================================

lint: lint-js lint-py

lint-js:
	@echo ""
	@echo "Linting JavaScript..."
	cd $(JS_DIR) && npm run lint

lint-py:
	@echo ""
	@echo "Linting Python..."
	cd $(PY_DIR) && poetry run ruff check src tests

# =============================================================================
# Clean Targets
# =============================================================================

clean:
	@echo "Cleaning artifacts..."
	rm -rf $(JS_DIR)/dist
	rm -rf $(JS_DIR)/node_modules
	rm -rf $(JS_DIR)/coverage
	rm -rf $(PY_DIR)/.pytest_cache
	rm -rf $(PY_DIR)/dist
	rm -rf $(PY_DIR)/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"
