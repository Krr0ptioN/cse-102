from __future__ import annotations

from core.db.connector import DBConnector
from libs.logger import get_logger


class Repository:
    def __init__(self, db: DBConnector) -> None:
        self.db = db
        self.log = get_logger(f"app.core.repositories.{self.__class__.__name__}")
        self.log.debug("Repository initialized")
