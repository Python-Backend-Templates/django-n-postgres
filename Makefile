PROJECT_NAME=django-n-postgres-template
SERVICE_NAME=wsgi

up:
	docker compose -f docker/docker-compose.yml -p $(PROJECT_NAME) up --remove-orphans
build:
	docker compose -f docker/docker-compose.yml -p $(PROJECT_NAME) build --no-cache
localup:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml -p $(PROJECT_NAME) up --remove-orphans
localbuild:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml -p $(PROJECT_NAME) build --no-cache
mainup:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.main.yml -p $(PROJECT_NAME) up --remove-orphans
mainbuild:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.main.yml -p $(PROJECT_NAME) build --no-cache
migrations:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} python manage.py makemigrations
migrate:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} python manage.py migrate
test:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} pytest .
lint:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} flake8 .
typecheck:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} mypy .
format:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} black .
sortimports:
	docker exec -it $(PROJECT_NAME)-${SERVICE_NAME} isort . --profile black --filter-files
