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
	$(PYTHON) manage.py sqlflush | $(PYTHON) manage.py dbshell

migrate-db:
	$(PYTHON) manage.py makemigrations $(NOINPUT_OPT)
	$(PYTHON) manage.py migrate --run-syncdb $(NOINPUT_OPT)

populate-db:
	$(PYTHON) manage.py loaddata fixtures/users.json
	$(PYTHON) manage.py loaddata fixtures/rooms.json
	$(PYTHON) manage.py loaddata fixtures/activities.json
	$(PYTHON) manage.py loaddata fixtures/events.json

reset-db: delete-db migrate-db populate-db

server:
	$(PYTHON) manage.py runserver
