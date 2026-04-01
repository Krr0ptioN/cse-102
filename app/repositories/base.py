from __future__ import annotations

from app.db.connector import DBConnector


class Repository:
    def __init__(self, db: DBConnector) -> None:
        self.db = db
