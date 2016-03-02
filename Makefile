SHELL := /bin/bash
PYTHON ?= python3
PIP ?= pip3
PEP8 ?= pep8
NOINPUT_OPT := $(shell if [ "$$NOINPUT" = true ]; then echo "--noinput"; fi)

default:
	@echo "Choose a target"

install:
	$(PIP) install -r requirements.txt

linter:
	$(PEP8) --exclude=migrations --config=.pep8 .

test:
	$(PYTHON) -Wall manage.py test

delete-db:
	rm -f db.sqlite3

delete-migrations:
	@# Currently we do not use migrations
	@shopt -s nullglob && \
	for f in */migrations/*.py; do \
		if [ "$$(basename "$$f")" != "__init__.py" ]; then \
			echo "Delete $$f"; \
			rm "$$f"; \
		fi; \
	done

migrate-db:
	$(PYTHON) manage.py makemigrations $(NOINPUT_OPT)
	$(PYTHON) manage.py migrate $(NOINPUT_OPT)

populate-db:
	$(PYTHON) manage.py loaddata fixtures/users.json
	$(PYTHON) manage.py loaddata fixtures/rooms.json
	$(PYTHON) manage.py loaddata fixtures/activities.json
	$(PYTHON) manage.py loaddata fixtures/events.json

reset-db: delete-db delete-migrations migrate-db populate-db

server:
	$(PYTHON) manage.py runserver
