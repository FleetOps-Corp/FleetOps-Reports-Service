# SAD Traceability: copy-pasteable developer commands required by the prompt.

.PHONY: up down test coverage lint import-linter mypy ruff validate

up:
	docker compose up --build

down:
	docker compose down

test:
	cd backend && pytest

coverage:
	cd backend && coverage run -m pytest tests/unit/domain tests/unit/application && coverage report && coverage html

import-linter:
	cd backend && lint-imports

mypy:
	cd backend && mypy

ruff:
	cd backend && ruff check src tests

lint: import-linter mypy ruff

validate: lint test coverage
