.PHONY: install start dev help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Runtime Template Resolver - Node.js Examples"
	@echo ""
	@echo "Available targets:"
	@echo "  install  - Install dependencies using npm"
	@echo "  start    - Run basic usage examples"
	@echo "  dev      - Run Fastify app in development mode"
	@echo ""

# Install dependencies (uses parent npm project)
install:
	@echo "Installing dependencies..."
	cd .. && npm install
	@echo "Installing tsx for running TypeScript..."
	cd .. && npm install -D tsx pino-pretty

# Run basic usage examples
start:
	@echo "Running basic usage examples..."
	cd .. && npx tsx examples/basic-usage.ts

# Run Fastify app in development mode
dev:
	@echo "Starting Fastify development server..."
	@echo "Server will be available at: http://localhost:3000"
	@echo "Try: curl http://localhost:3000/health"
	cd .. && npx tsx watch examples/fastify-app/server.ts
