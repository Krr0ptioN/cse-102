from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure local package imports work from any cwd.
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
for path in (APP_ROOT, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from core.db.schema import init_db
from libs.logger import get_logger


logger = get_logger("app.scripts.init_db")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize the SQLite schema")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "app.db",
        help="Path to the SQLite database (default: app/app.db)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger.banner("Database Init")
    logger.info("Target database: %s", args.db)
    init_db(str(args.db))
    logger.success("Initialized database schema at %s", args.db)


if __name__ == "__main__":
    main()
