PROJECT_NAME=django-n-postgres-template

localup:
	docker compose -f docker-compose.local.yml up --remove-orphans
localbuild:
	docker compose -f docker-compose.local.yml build --no-cache
developup:
	docker compose -f docker-compose.develop.yml up --remove-orphans
developbuild:
	docker compose -f docker-compose.develop.yml build --no-cache
test:
	docker exec -it $(PROJECT_NAME)-wsgi pytest .
flake8:
	docker exec -it $(PROJECT_NAME)-wsgi flake8 .
mypy:
	docker exec -it $(PROJECT_NAME)-wsgi mypy .
black:
	docker exec -it $(PROJECT_NAME)-wsgi black .
isort:
	docker exec -it $(PROJECT_NAME)-wsgi isort . --profile black --filter-files
