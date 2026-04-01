from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


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


def main() -> None:
    db_path = Path(__file__).resolve().parents[2] / "app.db"
    if not db_path.exists():
        print(f"No database found at {db_path}")
        return
    conn = sqlite3.connect(db_path)
    print(f"DB: {db_path}")
    for table in TABLES:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.Error as exc:
            print(f"{table}: error ({exc})")
            continue
        print(f"{table}: {count}")
    conn.close()


if __name__ == "__main__":
    main()
