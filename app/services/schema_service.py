from __future__ import annotations

from app.db.connector import DBConnector


def list_tables(db_path: str) -> list[str]:
    db = DBConnector(db_path)
    with db.connect() as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cur.fetchall()]
