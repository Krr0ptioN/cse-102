from __future__ import annotations

from app.db.connector import DBConnector


class SchemaService:
    def __init__(self, db_path: str) -> None:
        self.db = DBConnector(db_path)

    def list_tables(self) -> list[str]:
        with self.db.connect() as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cur.fetchall()]
