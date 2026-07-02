# SAD Traceability: developer commands for local development and CI.

.PHONY: \
	up down \
	test coverage \
	import-linter mypy ruff lint \
	bandit security \
	compose-validate \
	build-backend build-gateway build \
	validate release clean

up:
	docker compose up --build

down:
	docker compose down

test:
	cd backend && pytest

coverage:
	cd backend && \
		coverage run -m pytest tests/unit/domain tests/unit/application && \
		coverage xml && \
		coverage report && \
		coverage html
	python scripts/normalize_coverage_for_sonar.py

import-linter:
	cd backend && lint-imports

mypy:
	cd backend && mypy

ruff:
	cd backend && ruff check src tests

lint: import-linter mypy ruff

bandit:
	cd backend && bandit -r src -f json -o ../bandit-report.json

security: bandit

compose-validate:
	docker compose config
	docker compose -f docker-compose.prod.yml --env-file .env.production.example config

build-backend:
	docker build \
		-t fleetops-reports-backend:local \
		./backend

build-gateway:
	docker build \
		-t fleetops-reports-gateway:local \
		./gateway

build: \
	compose-validate \
	build-backend \
	build-gateway

validate: \
	lint \
	security \
	test \
	coverage

release: validate build

clean:
	rm -rf backend/htmlcov
	rm -f backend/.coverage
	rm -f backend/coverage.xml
	rm -f bandit-report.json