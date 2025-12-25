.PHONY: format lint typecheck check install

# =============================================
# Python
# =============================================
format-py:
	ruff format src/

lint-py:
	ruff check src/ --fix

typecheck-py:
	ty check src/pyreact_start/

# =============================================
# TypeScript - Library
# =============================================
format-ts:
	cd src/pyreact_start/ts && bun run format

lint-ts:
	cd src/pyreact_start/ts && bun run lint

typecheck-ts:
	cd src/pyreact_start/ts && bun run typecheck

# =============================================
# Combined Targets
# =============================================
format: format-py format-ts
lint: lint-py lint-ts
typecheck: typecheck-py typecheck-ts

# Full check including examples
check:
	./scripts/check-all.sh

# Quick check (library only, no examples)
check-lib: lint-py typecheck-py lint-ts typecheck-ts
