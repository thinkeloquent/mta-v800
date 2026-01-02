# =============================================================================
# app_yaml_overwrites - Node.js Examples Makefile
# =============================================================================

.PHONY: install start dev test clean help

# Default target
all: help

# =============================================================================
# Installation
# =============================================================================

install:
	@echo "Installing Node.js dependencies..."
	cd .. && npm install
	npm install tsx fastify

# =============================================================================
# Run Examples
# =============================================================================

start:
	@echo "Running basic usage examples..."
	npx tsx basic-usage.ts

dev:
	@echo "Starting Fastify development server on port 3000..."
	npx tsx watch fastify-app/server.ts

# =============================================================================
# Testing
# =============================================================================

test:
	@echo "Testing Fastify endpoints..."
	@echo ""
	@echo "Health check:"
	curl -s http://localhost:3000/health | npx json
	@echo ""
	@echo "Configuration:"
	curl -s http://localhost:3000/config | npx json
	@echo ""
	@echo "Context (with headers):"
	curl -s -H "Authorization: Bearer test-token" -H "X-Tenant-Id: tenant-123" \
		http://localhost:3000/context | npx json
	@echo ""
	@echo "Provider (raw):"
	curl -s http://localhost:3000/providers/userApi/raw | npx json
	@echo ""
	@echo "Provider (resolved with context):"
	curl -s -H "Authorization: Bearer my-jwt-token" -H "X-Tenant-Id: tenant-456" \
		-H "X-Request-Id: req-789" \
		http://localhost:3000/providers/userApi | npx json
	@echo ""
	@echo "Demo - All resolved headers:"
	curl -s -H "Authorization: Bearer demo-token" -H "X-Tenant-Id: demo-tenant" \
		http://localhost:3000/demo/resolved-headers | npx json

test-simple:
	@echo "Testing Fastify endpoints (without JSON formatting)..."
	@echo ""
	@echo "Health check:"
	curl -s http://localhost:3000/health
	@echo ""
	@echo "\nProvider (resolved):"
	curl -s -H "Authorization: Bearer my-jwt-token" -H "X-Tenant-Id: tenant-456" \
		http://localhost:3000/providers/userApi

# =============================================================================
# Clean
# =============================================================================

clean:
	@echo "Cleaning Node.js cache..."
	rm -rf node_modules 2>/dev/null || true

# =============================================================================
# Help
# =============================================================================

help:
	@echo "app_yaml_overwrites - Node.js Examples"
	@echo ""
	@echo "Usage:"
	@echo "  make install      Install dependencies"
	@echo "  make start        Run basic usage examples"
	@echo "  make dev          Start Fastify server (port 3000)"
	@echo "  make test         Test Fastify endpoints (requires server running)"
	@echo "  make test-simple  Test endpoints without JSON formatting"
	@echo "  make clean        Remove node_modules"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make install"
	@echo "  2. make start      # Run basic examples"
	@echo "  3. make dev        # Start server (in separate terminal)"
	@echo "  4. make test       # Test endpoints"
