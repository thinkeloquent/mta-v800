.PHONY: install start dev help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Runtime Template Resolver - Python Examples"
	@echo ""
	@echo "Available targets:"
	@echo "  install  - Install dependencies using poetry"
	@echo "  start    - Run basic usage examples"
	@echo "  dev      - Run FastAPI app in development mode"
	@echo ""

# Install dependencies (uses parent poetry project)
install:
	@echo "Installing dependencies..."
	cd .. && poetry install

# Run basic usage examples
start:
	@echo "Running basic usage examples..."
	cd .. && poetry run python examples/basic_usage.py

# Run FastAPI app in development mode
dev:
	@echo "Starting FastAPI development server..."
	@echo "API docs available at: http://localhost:8000/docs"
	cd .. && poetry run uvicorn examples.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
