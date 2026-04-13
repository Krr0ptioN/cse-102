PYTHON := python
UV := uv
UV_RUN := $(UV) run --python .venv/bin/python
PYTHONPATH := ..

.PHONY: setup install-dev install-build run test db-setup seed seed-semester seed-semester-noreset mock-setup db-status compile clean

setup:
	$(UV) venv --python 3.14 .venv
	$(UV) pip install -r requirements.txt

install-dev:
	$(UV) venv --python 3.14 .venv
	$(UV) pip install -r requirements.txt -r requirements-dev.txt

install-build:
	$(UV) venv --python 3.14 .venv
	$(UV) pip install -r requirements.txt -r requirements-build.txt

run:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) $(PYTHON) -m app.main

test:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) pytest

db-setup:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/init_db.py

seed:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/seed_mock_data.py --reset

seed-semester:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/seed_semester_mock_data.py --reset

seed-semester-noreset:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/seed_semester_mock_data.py

mock-setup: db-setup seed-semester db-status

db-status:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/db_status.py

compile: install-build
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) python scripts/build_release.py --clean

clean:
	rm -rf .venv
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
