from __future__ import annotations

from app.libs.logger import get_logger


class Service:
    def __init__(self, repo) -> None:
        self.repo = repo
        self.log = get_logger(f"app.core.services.{self.__class__.__name__}")
        self.log.debug("Service initialized")
