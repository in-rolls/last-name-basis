PY := .venv/bin/python
A01 := analyses/01_surname_to_category
A02 := analyses/02_jati_by_geography
A03 := analyses/03_how_few_names

all: a01 a02 a03

a01:
	$(PY) $(A01)/pipeline.py
	$(PY) $(A01)/note.py

a02:
	$(PY) $(A02)/pipeline.py
	$(PY) $(A02)/note.py

test:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/black --check --fast src analyses tests
	.venv/bin/isort --check-only src analyses tests
	.venv/bin/flake8 src analyses tests

fmt:
	.venv/bin/black --fast src analyses tests
	.venv/bin/isort src analyses tests

.PHONY: all a01 a02 a03 test lint fmt

a03:
	$(PY) $(A03)/pipeline.py
	$(PY) $(A03)/note.py
