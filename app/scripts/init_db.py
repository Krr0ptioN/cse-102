from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app.*` works when run from app/.
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.db.schema import init_db


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
    init_db(str(args.db))
    print(f"Initialized database schema at {args.db}")


if __name__ == "__main__":
    main()
