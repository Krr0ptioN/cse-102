from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_STORAGE_DIR = "CSE102ProjectManager"
DB_FILE_NAME = "app.db"


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


def ensure_local_db_path() -> Path:
    target = local_db_path()
    if target.exists():
        return target

    module_path = Path(__file__).resolve()
    legacy_candidates = [
        Path.cwd() / DB_FILE_NAME,
        module_path.parents[1] / DB_FILE_NAME,
        module_path.parents[2] / DB_FILE_NAME,
    ]

    for candidate in legacy_candidates:
        if candidate == target or not candidate.exists():
            continue
        try:
            shutil.copy2(candidate, target)
            break
        except OSError:
            continue

    return target
