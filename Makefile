.PHONY: up down logs migrate test test-unit test-integration lint format

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f ai-api

migrate:
	docker compose run --rm ai-api alembic upgrade head

test:
	pytest -q

test-unit:
	pytest -q -m "not integration"

test-integration:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner

down-test:
	docker compose -f docker-compose.test.yml down -v

lint:
	ruff check app tests

format:
	ruff format app tests
