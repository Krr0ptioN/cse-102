from __future__ import annotations

from app.services.base import Service


class SchemaService(Service):
    def __init__(self, db_path: str) -> None:
        super().__init__(db_path)

    def list_tables(self) -> list[str]:
        with self.db.connect() as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cur.fetchall()]
