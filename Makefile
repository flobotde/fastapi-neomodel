#!/usr/bin/make

include .env

define SERVERS_JSON
{
	"Servers": {
		"1": {
			"Name": "fastapi-neomodel",
			"Group": "Servers",
			"Host": "$(DATABASE_HOST)",
			"Port": 5432,
			"MaintenanceDB": "postgres",
			"Username": "$(DATABASE_USER)",
			"SSLMode": "prefer",
			"PassFile": "/tmp/pgpassfile"
		}
	}
}
endef
export SERVERS_JSON

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally."
	@echo "    run-dev-build"
	@echo "        Run development docker compose and force build containers."
	@echo "    run-dev"
	@echo "        Run development docker compose."
	@echo "    stop-dev"
	@echo "        Stop development docker compose."
	@echo "    run-prod"
	@echo "        Run production docker compose."
	@echo "    stop-prod"
	@echo "        Run production docker compose."
	@echo "    init-db"
	@echo "        Init database with sample data."	
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with ruff, and check if black formatter should be applied."
	@echo "    lint-watch"
	@echo "        Lint code with ruff in watch mode."
	@echo "    lint-fix"
	@echo "        Lint code with ruff and try to fix."	
	@echo "    run-sonarqube"
	@echo "        Starts Sonarqube container."
	@echo "    run-sonar-scanner"
	@echo "        Starts Sonarqube container."	
	@echo "    stop-sonarqube"
	@echo "        Stops Sonarqube container."

install:
	cd backend/app && \
	poetry shell && \
	poetry install

run-dev-build:
	docker compose -f docker-compose-dev.yml up --build

run-dev:
	docker compose -f docker-compose-dev.yml up

stop-dev:
	docker compose -f docker-compose-dev.yml down

run-prod:
	docker compose up

stop-prod:
	docker compose down

init-db:
	docker compose -f docker-compose-dev.yml exec fastapi_server python app/initial_data.py && \
	echo "Initial data created." 

formatter:
	cd backend/app && \
	poetry run black app

lint:
	cd backend/app && \
	poetry run ruff app && poetry run black --check app

mypy:
	cd backend/app && \
	poetry run mypy .

lint-watch:
	cd backend/app && \
	poetry run ruff app --watch

lint-fix:
	cd backend/app && \
	poetry run ruff app --fix

run-sonarqube:
	docker compose -f docker-compose-sonarqube.yml up

stop-sonarqube:
	docker compose -f docker-compose-sonarqube.yml down

run-sonar-scanner:
	docker run --rm -v "${PWD}/backend:/usr/src" sonarsource/sonar-scanner-cli -X

run-test:
	docker compose -f docker-compose-test.yml up --build

pytest:
	docker compose -f docker-compose-test.yml exec fastapi_server pytest
