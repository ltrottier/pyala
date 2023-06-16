.PHONY: venv test install-hooks pre-commit build

venv:
	python3.8 -m venv venv
	. venv/bin/activate
	pip install poetry
	poetry install

build:
	poetry build

test:
	poetry run pytest
	poetry run python scripts/transpile_tests.py
	cd scala; sbt test

pre-commit:
	poetry run pre-commit run --all-files

install-hooks:
	poetry run pre-commit install
