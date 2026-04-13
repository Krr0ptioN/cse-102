## Application

This directory is the root of the application codebase. All runtime code, tests, and tooling live here.

### Prerequisites
- Python 3.14+ (Tkinter included; install `python3-tk` via your OS package manager if missing)
- Linux/macOS: [uv](https://docs.astral.sh/uv/) + `make` (optional but recommended)
- Windows: PowerShell + Python launcher (`py` or `python`) (no uv required)

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
- Tasks: `setup`, `install-dev`, `install-build`, `run`, `test`, `db-setup`, `seed`, `db-status`, `compile`, `clean`.
- Additional mock-data tasks:
  - `seed-semester`: seeds the full semester mock dataset (`scripts/seed_semester_mock_data.py`)
  - `seed-semester-noreset` (Make only): same seeding without reset
  - `mock-setup`: `db-setup` + `seed-semester` + `db-status`
- `seed` and `seed-semester` reset the database by default. In PowerShell, use `-NoReset` to preserve existing data.

### Build Standalone Binary
Build on each target OS natively (no cross-compiling Windows from Linux or Linux from Windows):

```bash
cd app
make compile
```

```powershell
Set-Location app
.\make.ps1 compile
```

- Output artifact is created in `app/dist/`.
- Default name is `CSE102-App` (`CSE102-App.exe` on Windows).

### Local SQLite Storage
By default the app resolves the DB path based on runtime mode:

- Repo checkout / development: uses `app/app.db` (works directly with mock seeding scripts)
- Installed runtime: uses OS-local storage:
  - Windows: `%LOCALAPPDATA%\CSE102ProjectManager\app.db`
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/CSE102ProjectManager/app.db`
  - macOS: `~/Library/Application Support/CSE102ProjectManager/app.db`

You can override this behavior:

- `CSE102_DB_PATH=/absolute/or/relative/path/to/app.db` (or `APP_DB_PATH`) to force a specific DB file
- `CSE102_DB_MODE=dev|installed` (or `APP_DB_MODE`) to force mode selection

### Notes
- `PYTHONPATH=..` is set in the Makefile so imports like `app.services...` work when running from this directory.
- The PowerShell script sets the same `PYTHONPATH=..` behavior for Windows.
- Dependencies are split: runtime in `requirements.txt`, dev-only in `requirements-dev.txt`, build-only in `requirements-build.txt`.
