PYTHON := python3
DOCKER_COMPOSE := docker-compose -f docker-compose.test.yml
VENV := env/bin/

.PHONY: install run test lint setup-db test-coverage test-coverage-html unit-test integration-test

install:
	$(PYTHON) -m venv env
	$(VENV)pip install -r requirements.txt

run:
	$(VENV)python main.py

unit-test:
	TESTING=True $(VENV)python -m pytest -v tests/test_unit.py

integration-test:
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@$(DOCKER_COMPOSE) run --rm db sh -c 'while ! pg_isready -h db -p 5432 -U test_user -d test_db; do sleep 1; done'
	DB_HOST=localhost DB_PORT=5432 DB_NAME=test_db DB_USER=test_user DB_PASSWORD=test_password TESTING=True $(VENV)python -m pytest -v tests/test_integration.py
	$(DOCKER_COMPOSE) down

test: unit-test integration-test

lint:
	$(VENV)python -m ruff check

setup-db:
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	$(VENV)python -m src.db_setup

test-coverage:
	mkdir -p coverage_data
	chmod 777 coverage_data
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	DB_HOST=localhost DB_PORT=5432 DB_NAME=test_db DB_USER=test_user DB_PASSWORD=test_password TESTING=True $(VENV)python -m pytest --cov=src --cov-report=term-missing --cov-report=xml:coverage_data/coverage.xml tests/
	$(DOCKER_COMPOSE) down

test-coverage-html:
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	DB_HOST=localhost DB_PORT=5432 DB_NAME=test_db DB_USER=test_user DB_PASSWORD=test_password TESTING=True $(VENV)python -m pytest --cov=src --cov-report=html tests/
	$(DOCKER_COMPOSE) down
