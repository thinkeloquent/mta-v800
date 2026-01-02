.PHONY: install build clean test test-py test-mjs test-unit test-integration test-all lint example example-py example-mjs example-fastapi example-fastify

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
	cd $(PY_DIR) && poetry run pytest __tests__/test_compute_registry.py __tests__/test_security.py __tests__/test_context_resolver.py -v

test-py-integration:
	@echo "$(YELLOW)Running Python integration tests (FastAPI)...$(NC)"
	cd $(PY_DIR) && poetry run pytest __tests__/test_fastapi_integration.py -v

test-py-coverage:
	@echo "$(YELLOW)Running Python tests with coverage...$(NC)"
	cd $(PY_DIR) && poetry run pytest --cov=runtime_template_resolver --cov-report=html --cov-report=term

#------------------------------------------------------------------------------
# Testing - Node.js
#------------------------------------------------------------------------------

test-mjs: build-mjs test-mjs-unit test-mjs-integration
	@echo "$(GREEN)All Node.js tests passed!$(NC)"

test-mjs-unit:
	@echo "$(YELLOW)Running Node.js unit tests...$(NC)"
	cd $(MJS_DIR) && npx vitest run __tests__/compute-registry.test.ts __tests__/security.test.ts __tests__/context-resolver.test.ts

test-mjs-integration:
	@echo "$(YELLOW)Running Node.js integration tests (Fastify)...$(NC)"
	cd $(MJS_DIR) && npx vitest run __tests__/fastify-integration.test.ts

test-mjs-coverage:
	@echo "$(YELLOW)Running Node.js tests with coverage...$(NC)"
	cd $(MJS_DIR) && npm run test:coverage

#------------------------------------------------------------------------------
# Examples - Basic Usage
#------------------------------------------------------------------------------

example: example-py example-mjs
	@echo "$(GREEN)All examples completed!$(NC)"

example-py:
	@echo "$(YELLOW)Running Python basic usage example...$(NC)"
	cd $(PY_DIR) && poetry run python examples/basic_usage.py

example-mjs: build-mjs
	@echo "$(YELLOW)Running Node.js basic usage example...$(NC)"
	cd $(MJS_DIR) && npx tsx examples/basic-usage.ts

#------------------------------------------------------------------------------
# Examples - Framework Apps (Development Servers)
#------------------------------------------------------------------------------

example-fastapi:
	@echo "$(YELLOW)Starting FastAPI development server...$(NC)"
	@echo "$(GREEN)Visit http://localhost:8000/docs for API documentation$(NC)"
	cd $(PY_DIR) && poetry run uvicorn examples.fastapi_app.main:app --reload --port 8000

example-fastify: build-mjs
	@echo "$(YELLOW)Starting Fastify development server...$(NC)"
	@echo "$(GREEN)Visit http://localhost:3000/health for health check$(NC)"
	cd $(MJS_DIR) && npx tsx watch examples/fastify-app/server.ts

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
