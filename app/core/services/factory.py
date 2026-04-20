from __future__ import annotations

from core.db.connector import DBConnector
from core.repositories import (
    AppStateRepository,
    AuthRepository,
    ClassRepository,
    CheckinRepository,
    RoadmapRepository,
    TaskRepository,
    TeamRepository,
)
from .app_state import AppStateService
from .auth import AuthService
from .classes import ClassService
from .checkin import CheckinService
from .roadmap import RoadmapService
from .session import SessionService
from .task import TaskService
from .team import TeamService
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
