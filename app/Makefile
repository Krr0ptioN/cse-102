PYTHON := python
UV := uv
UV_RUN := $(UV) run --python .venv/bin/python
PYTHONPATH := ..

.PHONY: setup install-dev run test clean

setup:
	$(UV) venv .venv
	$(UV) pip install -r requirements.txt

install-dev:
	$(UV) venv .venv
	$(UV) pip install -r requirements.txt -r requirements-dev.txt

run:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) $(PYTHON) -m app.main

test:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) pytest

seed:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/seed_mock_data.py --reset

db-status:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/db_status.py

clean:
	rm -rf .venv
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
