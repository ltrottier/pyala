export JAVA_HOME := /usr/lib/jvm/java-11-openjdk-amd64
export JAVA := $(JAVA_HOME)/bin/java
export PATH := $(JAVA_HOME)/bin/:$(PATH)

.ONESHELL:
.PHONY:

venv:
	python3.10 -m venv venv
	. venv/bin/activate
	pip install poetry
	poetry install

build:
	. venv/bin/activate
	poetry build

clean-scala-main:
	rm scala/src/main/scala/*.scala

transpile-tests:
	. venv/bin/activate
	poetry run python scripts/transpile_tests.py

test: transpile-tests
	. venv/bin/activate
	poetry run pytest
	cd scala; sbt test

docker-build:
	docker build -t pyala:latest .

docker-it:
	docker run -it -e "TERM=xterm-256color" pyala:latest bash -l

docker-test: test-transpile-tests docker-build
	docker run -t -e "TERM=xterm-256color" pyala:latest

pre-commit:
	. venv/bin/activate
	poetry run pre-commit run --all-files

install-hooks:
	. venv/bin/activate
	poetry run pre-commit install
