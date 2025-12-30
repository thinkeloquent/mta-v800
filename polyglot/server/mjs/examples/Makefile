# Makefile for Node.js Server Examples

.PHONY: help install start dev clean

# Get the directory where Makefile is located
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PARENT_DIR := $(MAKEFILE_DIR)..

# Default port for development server
PORT ?= 8080

help:
	@echo "Node.js Server Examples"
	@echo ""
	@echo "Commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make start     - Run basic usage examples"
	@echo "  make dev       - Run Fastify app in development mode"
	@echo "  make clean     - Clean up temporary files"
	@echo ""
	@echo "Environment:"
	@echo "  PORT           - Server port (default: $(PORT))"
	@echo "  LOG_LEVEL      - Log level (default: info)"

# Install dependencies (uses parent package dependencies)
install:
	@echo "Installing dependencies..."
	cd $(PARENT_DIR) && npm install
	@echo "Dependencies installed."

# Run basic usage examples
start:
	@echo "Running basic usage examples..."
	cd $(MAKEFILE_DIR) && LOG_LEVEL=debug node basic-usage.mjs

# Run Fastify app in development mode
dev:
	@echo "Starting Fastify development server on port $(PORT)..."
	cd $(MAKEFILE_DIR) && PORT=$(PORT) LOG_LEVEL=debug node fastify-app/server.mjs

# Run with nodemon for auto-reload (if available)
dev-watch:
	@echo "Starting Fastify server with auto-reload on port $(PORT)..."
	cd $(MAKEFILE_DIR) && PORT=$(PORT) LOG_LEVEL=debug npx nodemon --watch fastify-app fastify-app/server.mjs

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	rm -rf $(MAKEFILE_DIR)node_modules 2>/dev/null || true
	@echo "Cleanup complete."
