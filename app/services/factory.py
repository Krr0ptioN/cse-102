from __future__ import annotations

from app.db.connector import DBConnector
from app.repositories.app_state_repository import AppStateRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.checkin_repository import CheckinRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.team_repository import TeamRepository
from app.services.app_state import AppStateService
from app.services.auth import AuthService
from app.services.classes import ClassService
from app.services.checkin import CheckinService
from app.services.roadmap import RoadmapService
from app.services.session import SessionService
from app.services.task import TaskService
from app.services.team import TeamService


class ServiceFactory:
    def __init__(self, db: DBConnector) -> None:
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
