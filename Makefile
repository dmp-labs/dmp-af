.PHONY: help docs-serve docs-build docs-build-strict docs-test

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# CI
CI_DAGGER_DIR := .ci

help: ## Show this help message
	@echo "$(BLUE)dmp-af Documentation Commands$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make docs-serve         # Start local dev server"
	@echo "  make docs-build         # Build documentation"
	@echo "  make docs-test          # Validate documentation"

docs-serve: ## Start local documentation development server (http://localhost:8000)
	@echo "$(BLUE)🚀 Starting documentation server...$(NC)"
	@echo "$(GREEN)📖 Open http://127.0.0.1:8000 in your browser$(NC)"
	@echo ""
	@dagger -m "$(CI_DAGGER_DIR)" call docs serve --port=8000 up --ports=8000:8000

docs-build: ## Build static documentation site
	@echo "$(BLUE)🔨 Building documentation...$(NC)"
	@dagger -m "$(CI_DAGGER_DIR)" call docs build export --path=./site
	@echo "$(GREEN)✅ Documentation built successfully$(NC)"
	@echo "Output: ./site/"

docs-build-strict: ## Build documentation with strict mode (fail on warnings)
	@echo "$(BLUE)🔨 Building documentation (strict mode)...$(NC)"
	@dagger -m "$(CI_DAGGER_DIR)" call docs build --strict=true export --path=./site
	@echo "$(GREEN)✅ Documentation built successfully (no warnings)$(NC)"
	@echo "Output: ./site/"

docs-test: ## Test documentation build (validates links and structure)
	@echo "$(BLUE)🧪 Testing documentation build...$(NC)"
	@dagger -m "$(CI_DAGGER_DIR)" call docs test
	@echo "$(GREEN)✅ Documentation test passed$(NC)"

docs-clean: ## Remove build artifacts
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	@rm -rf site
	@echo "$(GREEN)✅ Cleaned$(NC)"

# Shorthand aliases
serve: docs-serve ## Alias for docs-serve
build: docs-build ## Alias for docs-build
test: docs-test ## Alias for docs-test
