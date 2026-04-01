from __future__ import annotations

from app.repositories.base import Repository


class AppStateRepository(Repository):
    DATASET_MODE_KEY = "dataset_mode"

    def get_dataset_mode(self) -> str:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT value FROM app_metadata WHERE key = ? LIMIT 1",
                (self.DATASET_MODE_KEY,),
            ).fetchone()
        if row is None:
            return "real"
        value = row[0] or "real"
        if value not in {"mock", "real"}:
            return "real"
        return value

    def set_dataset_mode(self, mode: str) -> None:
        if mode not in {"mock", "real"}:
            raise ValueError("dataset mode must be 'mock' or 'real'")
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO app_metadata(key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (self.DATASET_MODE_KEY, mode),
            )
