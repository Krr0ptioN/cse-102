from __future__ import annotations

from app.db.connector import DBConnector
from app.services.classes import ClassService
from app.services.checkin import CheckinService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService


class ServiceFactory:
    def __init__(self, db: DBConnector) -> None:
        self.class_service = ClassService(db)
        self.checkin_service = CheckinService(db)
        self.team_service = TeamService(db)
        self.roadmap_service = RoadmapService(db)
        self.task_service = TaskService(db)
