from __future__ import annotations

from app.core.repositories.app_state_repository import AppStateRepository
from app.core.services.base import Service


class AppStateService(Service):
    def __init__(self, repo: AppStateRepository) -> None:
        super().__init__(repo)

    def get_dataset_mode(self) -> str:
        return self.repo.get_dataset_mode()

    def set_dataset_mode(self, mode: str) -> None:
        self.repo.set_dataset_mode(mode)
