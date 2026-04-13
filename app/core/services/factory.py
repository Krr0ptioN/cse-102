from __future__ import annotations

from app.core.db.connector import DBConnector
from app.core.repositories.app_state_repository import AppStateRepository
from app.core.repositories.auth_repository import AuthRepository
from app.core.repositories.class_repository import ClassRepository
from app.core.repositories.checkin_repository import CheckinRepository
from app.core.repositories.roadmap_repository import RoadmapRepository
from app.core.repositories.task_repository import TaskRepository
from app.core.repositories.team_repository import TeamRepository
from app.core.services.app_state import AppStateService
from app.core.services.auth import AuthService
from app.core.services.classes import ClassService
from app.core.services.checkin import CheckinService
from app.core.services.roadmap import RoadmapService
from app.core.services.session import SessionService
from app.core.services.task import TaskService
from app.core.services.team import TeamService
from app.libs.logger import get_logger


class ServiceFactory:
    def __init__(self, db: DBConnector) -> None:
        self.log = get_logger("app.core.services.factory")
        self.log.info("Initializing service factory")
        app_state_repo = AppStateRepository(db)
        auth_repo = AuthRepository(db)
        class_repo = ClassRepository(db)
        checkin_repo = CheckinRepository(db)
        team_repo = TeamRepository(db)
        roadmap_repo = RoadmapRepository(db)
        task_repo = TaskRepository(db)

        self.app_state_service = AppStateService(app_state_repo)
        self.auth_service = AuthService(auth_repo)
        self.class_service = ClassService(class_repo)
        self.checkin_service = CheckinService(checkin_repo)
        self.team_service = TeamService(team_repo)
        self.roadmap_service = RoadmapService(roadmap_repo)
        self.task_service = TaskService(task_repo)
        self.session_service = SessionService()
        self.log.success("Service factory initialized")
