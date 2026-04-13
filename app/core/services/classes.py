from __future__ import annotations

from app.core.services.base import Service
from app.core.repositories.class_repository import ClassRepository


class ClassService(Service):
    def __init__(self, repo: ClassRepository) -> None:
        super().__init__(repo)

    def create_class(
        self, name: str, term: str, owner_user_id: int | None = None
    ) -> int:
        return self.repo.create_class(name, term, owner_user_id)

    def create_user(self, name: str, email: str, role: str) -> int:
        return self.repo.create_user(name, email, role)

    def list_users(self, role: str | None = None) -> list[dict]:
        return self.repo.list_users(role)

    def update_user(self, user_id: int, name: str, email: str) -> None:
        self.repo.update_user(user_id, name, email)

    def delete_user(self, user_id: int) -> None:
        self.repo.delete_user(user_id)

    def list_classes(self, owner_user_id: int | None = None) -> list[dict]:
        return self.repo.list_classes(owner_user_id)
