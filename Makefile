.PHONY: venv test

venv:
	python3.8 -m venv venv
	. venv/bin/activate
	pip install poetry
	poetry install

test:
	poetry run pytest