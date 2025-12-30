# Development commands for polyglot/server

# Default ports
MJS_PORT ?= 53000
PY_PORT ?= 54000

# Get the directory where Makefile is located
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Use local .venv if it exists, otherwise use system Python
VENV_DIR := $(MAKEFILE_DIR)py/.venv
PYTHON := $(if $(wildcard $(VENV_DIR)/bin/python),$(VENV_DIR)/bin/python,python)

.PHONY: help install install-mjs install-py dev dev-mjs dev-py clean clean-ports

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
