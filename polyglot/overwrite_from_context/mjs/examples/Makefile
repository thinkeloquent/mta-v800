.PHONY: install start dev clean build

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m

install:
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	cd .. && npm install
	@echo "$(GREEN)Dependencies installed$(NC)"

build:
	@echo "$(YELLOW)Building TypeScript...$(NC)"
	cd .. && npm run build
	@echo "$(GREEN)Build complete$(NC)"

start: build
	@echo "$(YELLOW)Running basic usage example...$(NC)"
	cd .. && npx tsx examples/basic-usage.ts

dev: build
	@echo "$(YELLOW)Starting Fastify development server...$(NC)"
	cd .. && npx tsx watch examples/fastify-app/server.ts

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf ../dist
	@echo "$(GREEN)Cleanup complete$(NC)"
