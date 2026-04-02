## Application

This directory is the root of the application codebase. All runtime code, tests, and tooling live here.

### Prerequisites
- Python 3.11+ (Tkinter included; install `python3-tk` via your OS package manager if missing)
- [uv](https://docs.astral.sh/uv/) (Rust-based Python installer/runner)
- `make` (optional, for macOS/Linux task shortcuts)

### Quickstart (macOS/Linux)
```bash
cd app
curl -LsSf https://astral.sh/uv/install.sh | sh   # if uv not installed
make setup                                       # create .venv and install runtime deps
make run                                         # launch the Tkinter app
```

### Quickstart (Windows PowerShell)
```powershell
Set-Location app
uv --version
.\make.ps1 setup
.\make.ps1 run
```

### Development
```bash
cd app
make install-dev   # adds pytest
make test          # runs test suite with PYTHONPATH=.. for package resolution
```

```powershell
Set-Location app
.\make.ps1 install-dev
.\make.ps1 test
```

### Commands
- Use the same task names in both wrappers:
  - macOS/Linux: `make <task>`
  - Windows PowerShell: `.\make.ps1 <task>`
- Tasks: `setup`, `install-dev`, `run`, `test`, `db-setup`, `seed`, `db-status`, `clean`.
- `seed` resets the database by default (`--reset`). In PowerShell, use `.\make.ps1 seed -NoReset` to preserve existing data.

### Notes
- `PYTHONPATH=..` is set in the Makefile so imports like `app.services...` work when running from this directory.
- The PowerShell script sets the same `PYTHONPATH=..` behavior for Windows.
- Dependencies are split: runtime in `requirements.txt`, dev-only in `requirements-dev.txt`.
