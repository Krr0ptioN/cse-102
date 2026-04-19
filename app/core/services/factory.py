from __future__ import annotations

from core.db.connector import DBConnector
from core.repositories import AppStateRepository
from core.repositories import AuthRepository
from core.repositories import ClassRepository
from core.repositories import CheckinRepository
from core.repositories import RoadmapRepository
from core.repositories import TaskRepository
from core.repositories import TeamRepository
from core.services import AppStateService
from core.services import AuthService
from core.services import ClassService
from core.services import CheckinService
from core.services import RoadmapService
from core.services import SessionService
from core.services import TaskService
from core.services import TeamService
from libs.logger import get_logger


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
