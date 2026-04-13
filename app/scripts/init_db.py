from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app.*` works from any cwd.
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.db.schema import init_db
from app.libs.logger import get_logger


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
