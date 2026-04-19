from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.db.connector import DBConnector
from core.db.schema import init_db
from core.services import ServiceFactory
from libs.logger import get_logger


@dataclass(frozen=True)
class AppConfig:
    title: str
    geometry: str
    db_path: Path


@dataclass(frozen=True)
class AppRuntime:
    config: AppConfig
    services: ServiceFactory
    dataset_mode: str


class AppBootstrap:
    """Builds runtime configuration and initializes dependencies."""

    def __init__(
        self,
        *,
        db_path_resolver: Callable[[], Path],
        title: str = "Teacher-Student Assignment Dashboard",
        geometry: str = "1100x740",
    ) -> None:
        self._resolve_db_path = db_path_resolver
        self._title = title
        self._geometry = geometry
        self.log = get_logger("app.core.bootstrap")

    def load_config(self) -> AppConfig:
        db_path = Path(self._resolve_db_path())
        config = AppConfig(
            title=self._title,
            geometry=self._geometry,
            db_path=db_path,
        )
        self.log.info("Config loaded (db=%s)", config.db_path)
        return config

    def initialize(self) -> AppRuntime:
        config = self.load_config()
        self.log.info("Initializing schema and dependencies")
        init_db(str(config.db_path))
        services = ServiceFactory(DBConnector(str(config.db_path)))
        dataset_mode = services.app_state_service.get_dataset_mode()
        self.log.success("Bootstrap complete (dataset_mode=%s)", dataset_mode)
        return AppRuntime(config=config, services=services, dataset_mode=dataset_mode)
