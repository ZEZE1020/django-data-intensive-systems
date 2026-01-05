# Makefile for django-data-intensive-systems
#
# This Makefile provides a set of convenient shortcuts for common development tasks.
# Each command is designed to be run from the root of the project directory.

# Use bash for all recipes
SHELL := /bin/bash

# Default help target
.DEFAULT_GOAL := help

# Phony targets are not real files
.PHONY: help setup run stop logs migrate shell test clean update-deps

help:
	@echo "------------------------------------------------------------------"
	@echo " django-data-intensive-systems Makefile                          "
	@echo "------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help           : Show this help message."
	@echo "  setup          : Build docker containers and setup the environment."
	@echo "  run            : Start all services in detached mode."
	@echo "  stop           : Stop all running services."
	@echo "  logs           : View logs from all services."
	@echo "  migrate        : Run Django database migrations."
	@echo "  makemigrations : Create new Django database migrations."
	@echo "  shell          : Start a Django shell inside the web container."
	@echo "  test           : Run the pytest test suite."
	@echo "  lint           : Run linters (black, isort, flake8)."
	@echo "  update-deps    : Update requirements.txt files from .in files."
	@echo "  clean          : Remove docker containers, volumes, and networks."
	@echo "------------------------------------------------------------------"

setup:
	@echo "--- Building Docker images and setting up environment ---"
	@docker-compose build
	@echo "--- Setup complete ---"

run:
	@echo "--- Starting all services in detached mode ---"
	@docker-compose up -d

stop:
	@echo "--- Stopping all services ---"
	@docker-compose down

logs:
	@echo "--- Tailing logs from all services (Ctrl+C to exit) ---"
	@docker-compose logs -f

migrate:
	@echo "--- Applying database migrations ---"
	@docker-compose exec web python manage.py migrate

makemigrations:
	@echo "--- Creating new database migrations ---"
	@docker-compose exec web python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

shell:
	@echo "--- Starting Django shell ---"
	@docker-compose exec web python manage.py shell

test:
	@echo "--- Running test suite ---"
	@docker-compose exec web pytest

lint:
	@echo "--- Running linters ---"
	@docker-compose exec web black . --check
	@docker-compose exec web isort . --check-only
	@docker-compose exec web flake8 .

update-deps:
	@echo "--- Updating requirements files ---"
	uv pip compile requirements/base.in -o requirements/base.txt
	uv pip compile requirements/dev.in -o requirements/dev.txt
	uv pip compile requirements/prod.in -o requirements/prod.txt
	uv pip compile requirements/test.in -o requirements/test.txt
	@echo "--- Requirements files updated ---"

clean:
	@echo "--- Removing all Docker containers, volumes, and networks ---"
	@docker-compose down -v --remove-orphans
	@echo "--- Clean complete ---"
