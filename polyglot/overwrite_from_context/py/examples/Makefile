.PHONY: install start dev clean

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m

install:
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	cd .. && poetry install
	@echo "$(GREEN)Dependencies installed$(NC)"

start:
	@echo "$(YELLOW)Running basic usage example...$(NC)"
	cd .. && poetry run python examples/basic_usage.py

dev:
	@echo "$(YELLOW)Starting FastAPI development server...$(NC)"
	cd .. && poetry run uvicorn examples.fastapi_app.main:app --reload --port 8000

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(NC)"
