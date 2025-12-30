# Makefile for Python Server Examples

.PHONY: help install start dev clean

# Get the directory where Makefile is located
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PARENT_DIR := $(MAKEFILE_DIR)..

# Use local .venv if it exists, otherwise use system Python
VENV_DIR := $(PARENT_DIR)/.venv
PYTHON := $(if $(wildcard $(VENV_DIR)/bin/python),$(VENV_DIR)/bin/python,python)

# Default port for development server
PORT ?= 8080

help:
	@echo "Python Server Examples"
	@echo ""
	@echo "Commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make start     - Run basic usage examples"
	@echo "  make dev       - Run FastAPI app in development mode"
	@echo "  make clean     - Clean up temporary files"
	@echo ""
	@echo "Environment:"
	@echo "  PORT           - Server port (default: $(PORT))"
	@echo "  LOG_LEVEL      - Log level (default: info)"

# Install dependencies (uses parent package dependencies)
install:
	@echo "Installing dependencies..."
	cd $(PARENT_DIR) && poetry install --no-root
	@echo "Dependencies installed."

# Run basic usage examples
start:
	@echo "Running basic usage examples..."
	cd $(MAKEFILE_DIR) && PYTHONPATH=$(PARENT_DIR)/app:$(PYTHONPATH) $(PYTHON) basic_usage.py

# Run FastAPI app in development mode
dev:
	@echo "Starting FastAPI development server on port $(PORT)..."
	cd $(MAKEFILE_DIR) && \
		PYTHONPATH=$(PARENT_DIR)/app:$(PYTHONPATH) \
		PORT=$(PORT) \
		$(PYTHON) -m uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port $(PORT)

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find $(MAKEFILE_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(MAKEFILE_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete."
