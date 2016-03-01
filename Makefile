PYTHON ?= python3
PIP ?= pip3
PEP8 ?= pep8
NOINPUT_OPT := $(shell if [ "$$NOINPUT" = true ]; then echo "--noinput"; fi)

default:
	@echo "Choose a target"

install:
	$(PIP) install -r requirements.txt

linter:
	$(PEP8) --exclude=migrations .

test:
	$(PYTHON) -Wall manage.py test

delete-db:
	$(PYTHON) manage.py flush $(NOINPUT_OPT)

migrate-db:
	$(PYTHON) manage.py makemigrations $(NOINPUT_OPT)
	$(PYTHON) manage.py migrate $(NOINPUT_OPT)

populate-db:
	$(PYTHON) manage.py loaddata fixtures/user.json
	$(PYTHON) manage.py loaddata fixtures/place.json
	$(PYTHON) manage.py loaddata fixtures/activity.json
	$(PYTHON) manage.py loaddata fixtures/event.json

reset-db: delete-db migrate-db prepare-db

server:
	$(PYTHON) manage.py runserver
