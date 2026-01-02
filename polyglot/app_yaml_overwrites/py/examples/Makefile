# =============================================================================
# app_yaml_overwrites - Python Examples Makefile
# =============================================================================

.PHONY: install start dev test clean help

# Default target
all: help

# =============================================================================
# Installation
# =============================================================================

install:
	@echo "Installing Python dependencies..."
	cd .. && pip install -e ".[dev]"
	pip install uvicorn httpx

# =============================================================================
# Run Examples
# =============================================================================

start:
	@echo "Running basic usage examples..."
	python basic_usage.py

dev:
	@echo "Starting FastAPI development server on port 8000..."
	uvicorn fastapi_app.main:app --reload --port 8000

# =============================================================================
# Testing
# =============================================================================

test:
	@echo "Testing FastAPI endpoints..."
	@echo ""
	@echo "Health check:"
	curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@echo "Configuration:"
	curl -s http://localhost:8000/config | python -m json.tool
	@echo ""
	@echo "Context (with headers):"
	curl -s -H "Authorization: Bearer test-token" -H "X-Tenant-Id: tenant-123" \
		http://localhost:8000/context | python -m json.tool
	@echo ""
	@echo "Provider (raw):"
	curl -s http://localhost:8000/providers/user_api/raw | python -m json.tool
	@echo ""
	@echo "Provider (resolved with context):"
	curl -s -H "Authorization: Bearer my-jwt-token" -H "X-Tenant-Id: tenant-456" \
		-H "X-Request-Id: req-789" \
		http://localhost:8000/providers/user_api | python -m json.tool

# =============================================================================
# Clean
# =============================================================================

clean:
	@echo "Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# Help
# =============================================================================

help:
	@echo "app_yaml_overwrites - Python Examples"
	@echo ""
	@echo "Usage:"
	@echo "  make install   Install dependencies"
	@echo "  make start     Run basic usage examples"
	@echo "  make dev       Start FastAPI server (port 8000)"
	@echo "  make test      Test FastAPI endpoints (requires server running)"
	@echo "  make clean     Remove cache files"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make install"
	@echo "  2. make start    # Run basic examples"
	@echo "  3. make dev      # Start server (in separate terminal)"
	@echo "  4. make test     # Test endpoints"
