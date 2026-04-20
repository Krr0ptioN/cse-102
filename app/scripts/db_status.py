from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

# Ensure local package imports work from any cwd.
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
for path in (APP_ROOT, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from libs.logger import get_logger


logger = get_logger("app.scripts.db_status")


TABLES = [
    "classes",
    "users",
    "teams",
    "team_members",
    "team_invitations",
    "roadmaps",
    "phases",
    "tasks",
    "updates",
    "roadmap_comments",
    "checkins",
    "checkin_comments",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print row counts for all core tables")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "app.db",
        help="Path to the SQLite database (default: app/app.db)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = args.db
    logger.banner("Database Status")
    if not db_path.exists():
        logger.warning("No database found at %s", db_path)
        return
    conn = sqlite3.connect(db_path)
    logger.info("DB: %s", db_path)
    for table in TABLES:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.Error as exc:
            logger.error("%s: error (%s)", table, exc)
            continue
        logger.info("%s: %s", table, count)
    conn.close()


if __name__ == "__main__":
    main()
