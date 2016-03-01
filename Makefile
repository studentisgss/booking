PYTHON ?= python3
PIP ?= pip3
PEP8 ?= pep8

install:
	$(PIP) install -r requirements.txt

linter:
	$(PEP8) --exclude=migrations .

test:
	$(PYTHON) -Wall manage.py test

prepare-db:
	$(PYTHON) manage.py makemigrations --noinput
	$(PYTHON) manage.py migrate --noinput
	$(PYTHON) manage.py loaddata fixtures/user.json
	$(PYTHON) manage.py loaddata fixtures/place.json

delete-db:
	$(PYTHON) manage.py flush

reset-db: delete-db prepare-db

server:
	$(PYTHON) manage.py runserver
