.PHONY: install build clean test test-py test-mjs test-unit test-integration test-all lint

# Directory paths
PY_DIR := py
MJS_DIR := mjs
FIXTURES_DIR := __fixtures__

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

#------------------------------------------------------------------------------
# Installation
#------------------------------------------------------------------------------

install: install-py install-mjs
	@echo "$(GREEN)All dependencies installed successfully$(NC)"

install-py:
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	cd $(PY_DIR) && poetry install

install-mjs:
	@echo "$(YELLOW)Installing Node.js dependencies...$(NC)"
	cd $(MJS_DIR) && npm install

#------------------------------------------------------------------------------
# Build
#------------------------------------------------------------------------------

build: build-mjs
	@echo "$(GREEN)Build completed successfully$(NC)"

build-mjs:
	@echo "$(YELLOW)Building Node.js package...$(NC)"
	cd $(MJS_DIR) && npm run build

#------------------------------------------------------------------------------
# Testing - All Tests
#------------------------------------------------------------------------------

test: test-py test-mjs
	@echo "$(GREEN)All tests passed!$(NC)"

test-all: build test
	@echo "$(GREEN)Build and all tests completed successfully$(NC)"

#------------------------------------------------------------------------------
# Testing - Python
#------------------------------------------------------------------------------

test-py: test-py-unit test-py-integration
	@echo "$(GREEN)All Python tests passed!$(NC)"

test-py-unit:
	@echo "$(YELLOW)Running Python unit tests...$(NC)"
	cd $(PY_DIR) && poetry run pytest __tests__/test_core.py __tests__/test_sdk.py __tests__/test_validators.py __tests__/test_logger.py -v

test-py-integration:
	@echo "$(YELLOW)Running Python FastAPI integration tests...$(NC)"
	cd $(PY_DIR) && poetry run pytest __tests__/test_api_integration.py -v

test-py-coverage:
	@echo "$(YELLOW)Running Python tests with coverage...$(NC)"
	cd $(PY_DIR) && poetry run pytest --cov=app_yaml_static_config --cov-report=html --cov-report=term

#------------------------------------------------------------------------------
# Testing - Node.js
#------------------------------------------------------------------------------

test-mjs: build-mjs test-mjs-unit test-mjs-integration
	@echo "$(GREEN)All Node.js tests passed!$(NC)"

test-mjs-unit:
	@echo "$(YELLOW)Running Node.js unit tests...$(NC)"
	cd $(MJS_DIR) && npm run test -- __tests__/core.test.mjs __tests__/sdk.test.mjs __tests__/validators.test.mjs __tests__/logger.test.mjs

test-mjs-integration:
	@echo "$(YELLOW)Running Node.js Fastify integration tests...$(NC)"
	cd $(MJS_DIR) && npm run test -- __tests__/api.integration.test.mjs

test-mjs-coverage:
	@echo "$(YELLOW)Running Node.js tests with coverage...$(NC)"
	cd $(MJS_DIR) && npm run test:coverage

#------------------------------------------------------------------------------
# Testing - By Category
#------------------------------------------------------------------------------

test-unit: test-py-unit test-mjs-unit
	@echo "$(GREEN)All unit tests passed!$(NC)"

test-integration: test-py-integration test-mjs-integration
	@echo "$(GREEN)All integration tests passed!$(NC)"

#------------------------------------------------------------------------------
# Testing - Framework Specific
#------------------------------------------------------------------------------

test-fastapi:
	@echo "$(YELLOW)Running FastAPI integration tests...$(NC)"
	cd $(PY_DIR) && poetry run pytest __tests__/test_api_integration.py -v

test-fastify: build-mjs
	@echo "$(YELLOW)Running Fastify integration tests...$(NC)"
	cd $(MJS_DIR) && npm run test -- __tests__/api.integration.test.mjs

#------------------------------------------------------------------------------
# Clean
#------------------------------------------------------------------------------

clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf $(MJS_DIR)/dist
	rm -rf $(MJS_DIR)/node_modules
	rm -rf $(PY_DIR)/.pytest_cache
	rm -rf $(PY_DIR)/htmlcov
	rm -rf $(MJS_DIR)/coverage
	find $(PY_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(PY_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean completed$(NC)"

#------------------------------------------------------------------------------
# Development
#------------------------------------------------------------------------------

watch-mjs:
	@echo "$(YELLOW)Running Node.js tests in watch mode...$(NC)"
	cd $(MJS_DIR) && npm run test:watch

#------------------------------------------------------------------------------
# Help
#------------------------------------------------------------------------------

help:
	@echo "Available targets:"
	@echo ""
	@echo "  $(GREEN)install$(NC)            - Install all dependencies (Python + Node.js)"
	@echo "  $(GREEN)build$(NC)              - Build all packages"
	@echo "  $(GREEN)test$(NC)               - Run all tests"
	@echo "  $(GREEN)test-all$(NC)           - Build and run all tests"
	@echo ""
	@echo "  $(YELLOW)Python Tests:$(NC)"
	@echo "    test-py           - Run all Python tests"
	@echo "    test-py-unit      - Run Python unit tests only"
	@echo "    test-py-integration - Run Python FastAPI tests"
	@echo "    test-py-coverage  - Run Python tests with coverage"
	@echo "    test-fastapi      - Run FastAPI integration tests"
	@echo ""
	@echo "  $(YELLOW)Node.js Tests:$(NC)"
	@echo "    test-mjs          - Run all Node.js tests"
	@echo "    test-mjs-unit     - Run Node.js unit tests only"
	@echo "    test-mjs-integration - Run Node.js Fastify tests"
	@echo "    test-mjs-coverage - Run Node.js tests with coverage"
	@echo "    test-fastify      - Run Fastify integration tests"
	@echo ""
	@echo "  $(YELLOW)By Category:$(NC)"
	@echo "    test-unit         - Run all unit tests"
	@echo "    test-integration  - Run all integration tests"
	@echo ""
	@echo "  $(YELLOW)Other:$(NC)"
	@echo "    clean             - Remove build artifacts"
	@echo "    watch-mjs         - Run Node.js tests in watch mode"
	@echo "    help              - Show this help message"
