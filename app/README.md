## Application

This directory is the root of the application codebase. All runtime code, tests, and tooling live here.

### Prerequisites
- Python 3.11+ (Tkinter included; install `python3-tk` via your OS package manager if missing)
- [uv](https://docs.astral.sh/uv/) (Rust-based Python installer/runner)

### Quickstart
```bash
cd app
curl -LsSf https://astral.sh/uv/install.sh | sh   # if uv not installed
make setup                                       # create .venv and install runtime deps
make run                                         # launch the Tkinter app
```

### Development
```bash
cd app
make install-dev   # adds pytest
make test          # runs test suite with PYTHONPATH=.. for package resolution
```

### Commands
- `make setup` — create `.venv` with runtime deps (`requirements.txt`).
- `make install-dev` — runtime + dev deps (`requirements-dev.txt`).
- `make run` — start the GUI (`python -m app.main`).
- `make test` — run pytest in `app/tests`.
- `python scripts/db_status.py` — print row counts for all tables (run from `app/`).
- `make clean` — remove `.venv` and `__pycache__`.

### Notes
- `PYTHONPATH=..` is set in the Makefile so imports like `app.services...` work when running from this directory.
- Dependencies are split: runtime in `requirements.txt`, dev-only in `requirements-dev.txt`.
