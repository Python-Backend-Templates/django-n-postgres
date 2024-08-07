localup:
	docker compose -f docker-compose.local.yml up --remove-orphans
localbuild:
	docker compose -f docker-compose.local.yml build --no-cache
developup:
	docker compose -f docker-compose.develop.yml up --remove-orphans
developbuild:
	docker compose -f docker-compose.develop.yml build --no-cache
pytest:
	docker exec -it wsgi pytest .
flake8:
	docker exec -it wsgi flake8.
mypy:
	docker exec -it wsgi mypy .
