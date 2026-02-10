from __future__ import annotations

from app.db.connector import DBConnector


class Service:
    def __init__(self, db_path: str) -> None:
        self.db = DBConnector(db_path)
