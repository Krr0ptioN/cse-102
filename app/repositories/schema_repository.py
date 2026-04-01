from __future__ import annotations

from app.repositories.base import Repository


class SchemaRepository(Repository):
    def list_tables(self) -> list[str]:
        with self.db.connect() as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cur.fetchall()]
