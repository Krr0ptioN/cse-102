from __future__ import annotations

import os
import sqlite3
import shutil
import sys
from pathlib import Path


APP_STORAGE_DIR = "CSE102ProjectManager"
DB_FILE_NAME = "app.db"
DB_PATH_ENV_VARS = ("CSE102_DB_PATH", "APP_DB_PATH")
DB_MODE_ENV_VARS = ("CSE102_DB_MODE", "APP_DB_MODE")


def user_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg_data_home = os.getenv("XDG_DATA_HOME")
        if xdg_data_home:
            base = Path(xdg_data_home)
        else:
            base = Path.home() / ".local" / "share"

    path = base / APP_STORAGE_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def local_db_path() -> Path:
    return user_data_dir() / DB_FILE_NAME


def project_db_path() -> Path:
    module_path = Path(__file__).resolve()
    return module_path.parents[2] / DB_FILE_NAME


def _repo_root() -> Path:
    module_path = Path(__file__).resolve()
    return module_path.parents[3]


def _is_repo_checkout() -> bool:
    return (_repo_root() / ".git").exists()


def _candidate_seed_db_paths() -> list[Path]:
    module_path = Path(__file__).resolve()
    raw_candidates = [
        project_db_path(),  # app/app.db
        Path.cwd() / "app" / DB_FILE_NAME,
        Path.cwd() / DB_FILE_NAME,
        module_path.parents[3] / DB_FILE_NAME,
    ]
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in raw_candidates:
        if candidate in seen:
            continue
        unique.append(candidate)
        seen.add(candidate)
    return unique


def _normalize_db_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def _resolve_env_db_path() -> Path | None:
    for var_name in DB_PATH_ENV_VARS:
        raw = os.getenv(var_name, "").strip()
        if not raw:
            continue
        path = _normalize_db_path(raw)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Keep going: caller may still be able to read an existing file.
            pass
        return path
    return None


def _resolve_db_mode() -> str:
    for var_name in DB_MODE_ENV_VARS:
        raw = os.getenv(var_name, "").strip().lower()
        if not raw:
            continue
        if raw in {"dev", "development"}:
            return "dev"
        if raw in {"installed", "install", "prod", "production"}:
            return "installed"
    return "auto"


def _db_has_login_accounts(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with sqlite3.connect(str(path)) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
            if "password_hash" not in cols or "password_salt" not in cols:
                return False
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM users
                WHERE COALESCE(is_active, 1) = 1
                  AND password_hash IS NOT NULL
                  AND password_salt IS NOT NULL
                  AND length(trim(password_hash)) > 0
                  AND length(trim(password_salt)) > 0
                """
            ).fetchone()
            return bool(row and int(row[0]) > 0)
    except sqlite3.Error:
        return False


def _sync_from_candidates(target: Path, candidates: list[Path]) -> bool:
    for candidate in candidates:
        if candidate == target or not candidate.exists():
            continue
        if not _db_has_login_accounts(candidate):
            continue
        try:
            shutil.copy2(candidate, target)
            return True
        except OSError:
            continue
    return False


def _resolve_dev_db_path() -> Path:
    for candidate in _candidate_seed_db_paths():
        if candidate.exists():
            return candidate
    return project_db_path()


def _resolve_installed_db_path() -> Path:
    target = local_db_path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # If user storage is not writable in this environment, fall back to project DB.
        return _resolve_dev_db_path()

    if target.exists():
        return target

    candidates = _candidate_seed_db_paths()

    # Prefer copying an existing credentialed seed DB.
    if _sync_from_candidates(target, candidates):
        return target

    # Fallback: copy first existing DB even if it has no login accounts yet.
    for candidate in candidates:
        if candidate == target or not candidate.exists():
            continue
        try:
            shutil.copy2(candidate, target)
            break
        except OSError:
            continue

    return target


def ensure_local_db_path() -> Path:
    # 1) Explicit path override always wins.
    env_path = _resolve_env_db_path()
    if env_path is not None:
        return env_path

    # 2) Explicit mode override.
    mode = _resolve_db_mode()
    if mode == "dev":
        return _resolve_dev_db_path()
    if mode == "installed":
        return _resolve_installed_db_path()

    # 3) Auto mode:
    #    - repo checkout => use project DB (best for local development and mock seeding)
    #    - installed runtime => use OS-local DB
    if _is_repo_checkout():
        return _resolve_dev_db_path()
    return _resolve_installed_db_path()
