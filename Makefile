SHELL := /bin/bash
PYTHON ?= python3
PIP ?= pip3
PYCODESTYLE ?= $(PYTHON) -m pycodestyle
FLAKE8 ?= $(PYTHON) -m flake8
PYLINT ?= $(PYTHON) -m pylint
NOINPUT_OPT := $(shell if [ "$$NOINPUT" = true ]; then echo "--noinput"; fi)

SRC_FILES := $(shell find . -name "*.py" -not -path "*/migrations/*")

default:
	@echo "Choose a target"

install:
	$(PIP) install -r requirements.txt

linter:
	@echo "=== Pycodestyle ==="
	@$(PYCODESTYLE) --max-line-length=180 --ignore=E722 $(SRC_FILES)
	@echo "=== Flake8 ==="
	@$(FLAKE8) --max-line-length=180 --ignore=E251,E265,E722,F401,F403,F405,F811,F999 \
		$(SRC_FILES)
	@echo "=== Pylint (really pedantic) ==="
	@$(PYLINT) --output-format=colorized --reports=no --persistent=n \
		--max-line-length=180 --ignored-modules=django \
		--disable=bad-builtin,missing-docstring,wildcard-import \
		--disable=too-many-locals,too-many-branches,unused-wildcard-import \
		--disable=too-many-statements,unused-import,star-args \
		--disable=duplicate-code,invalid-name,wrong-import-order \
		--disable=ungrouped-imports,broad-except,too-many-arguments \
		--disable=no-member,too-few-public-methods,too-many-ancestors \
		--disable=pointless-string-statement,unused-argument \
		$(SRC_FILES) \
		|| true
	@echo "=== Done ==="

test:
	$(PYTHON) -Wall manage.py test --logging-clear-handlers

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
	$(PYTHON) manage.py loaddata fixtures/groups.json
	$(PYTHON) manage.py loaddata fixtures/users.json
	$(PYTHON) manage.py loaddata fixtures/buildings.json
	$(PYTHON) manage.py loaddata fixtures/rooms.json
	$(PYTHON) manage.py loaddata fixtures/roomRules.json
	$(PYTHON) manage.py loaddata fixtures/roomPermissions.json
	$(PYTHON) manage.py loaddata fixtures/activities.json
	$(PYTHON) manage.py loaddata fixtures/events.json
	$(PYTHON) manage.py loaddata fixtures/news.json

reset-db: delete-db delete-migrations migrate-db populate-db

server:
	$(PYTHON) manage.py runserver

superuser:
		$(PYTHON) manage.py createsuperuser

internationalization:
	@for d in $$( ls -d */ | cut -f1 -d'/' ); do \
		cd $$d; \
		if [ -d "locale" ]; then \
			echo "Processing app $$d..."; \
			django-admin compilemessages; \
		fi; \
		cd ..; \
	done;
