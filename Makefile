PYTHON := python3
DOCKER_COMPOSE := docker-compose -f docker-compose.test.yml

.PHONY: install run test lint setup-db test-coverage test-coverage-html unit-test integration-test test-workflow test-workflow-push test-workflow-pr test-workflow-build

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py

unit-test:
	TESTING=True $(PYTHON) -m pytest -v tests/test_unit.py

integration-test:
	@echo "Running integration tests with Docker..."
	@echo "If this fails, please ensure Docker is installed and running,"
	@echo "and that the Docker CLI is available in your system PATH."
	$(DOCKER_COMPOSE) up --build --exit-code-from test || \
	(echo "Docker command failed. Is Docker installed and running?" && exit 1)

test: unit-test integration-test

lint:
	$(PYTHON) -m flake8 .

setup-db:
	docker-compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	DB_HOST=localhost DB_PORT=5432 $(PYTHON) -m src.db_setup
	docker-compose down

test-coverage:
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	$(DOCKER_COMPOSE) run --name telegram-referral-bot_test_run test pytest --cov=src --cov-report=term-missing --cov-report=xml:/tmp/coverage.xml tests/
	$(DOCKER_COMPOSE) down

test-coverage-html:
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	$(DOCKER_COMPOSE) run --rm test pytest --cov=src --cov-report=html tests/
	$(DOCKER_COMPOSE) down