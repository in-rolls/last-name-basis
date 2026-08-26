PY := .venv/bin/python

all: build

build:
	$(PY) scripts/build.py

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/black --check src scripts tests
	.venv/bin/isort --check-only src scripts tests
	.venv/bin/flake8 src scripts tests

fmt:
	.venv/bin/black src scripts tests
	.venv/bin/isort src scripts tests

.PHONY: all build note test lint fmt

note:
	$(PY) scripts/note.py

