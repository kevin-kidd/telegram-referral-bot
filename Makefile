PYTHON := python3
DOCKER_COMPOSE := docker-compose -f docker-compose.test.yml

.PHONY: install run test lint setup-db test-coverage test-coverage-html unit-test integration-test

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py

unit-test:
	$(PYTHON) -m pytest -v tests/test_unit.py

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
	@if [ "$(MAKECMDGOALS)" = "integration-test" ] || [ "$(MAKECMDGOALS)" = "test-coverage" ] || [ "$(MAKECMDGOALS)" = "test-coverage-html" ]; then \
		$(DOCKER_COMPOSE) up -d db; \
		DB_HOST=db $(PYTHON) -m src.db_setup; \
		$(DOCKER_COMPOSE) down; \
	else \
		docker-compose up -d db; \
		DB_HOST=localhost $(PYTHON) -m src.db_setup; \
		docker-compose down; \
	fi

test-coverage: setup-db
	$(DOCKER_COMPOSE) up -d db
	TESTING=True $(PYTHON) -m pytest --cov=src --cov-report=term-missing tests/
	$(DOCKER_COMPOSE) down

test-coverage-html: setup-db
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	TESTING=True $(PYTHON) -m pytest --cov=src --cov-report=html tests/
	$(DOCKER_COMPOSE) down