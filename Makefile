MANAGE = poetry run python src/manage.py

.PHONY: help runserver test createsuperuser csu makemigrations mm migrate mig updb

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  runserver		: Run the development server"
	@echo "  test			: Run tests"
	@echo "  createsuperuser, csu	: Create a superuser"
	@echo "  makemigrations, mm	: Create new migrations"
	@echo "  migrate, mig		: Apply migrations to the database"

runserver:
	$(MANAGE) migrate
	$(MANAGE) runserver

test:
	$(MANAGE) test src/apps/*/tests/

createsuperuser csu:
	$(MANAGE) createsuperuser

makemigrations mm:
	$(MANAGE) makemigrations

migrate mig:
	$(MANAGE) migrate

updb:
	$(MANAGE) makemigrations
	$(MANAGE) migrate
