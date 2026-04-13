from __future__ import annotations

from app.core.repositories.schema_repository import SchemaRepository
from app.core.services.base import Service


class SchemaService(Service):
    def __init__(self, repo: SchemaRepository) -> None:
        super().__init__(repo)

    def list_tables(self) -> list[str]:
        return self.repo.list_tables()
