from __future__ import annotations

from datetime import UTC, datetime

from app.repositories.team_repository import TeamRepository
from app.services.base import Service


class TeamService(Service):
    def __init__(self, repo: TeamRepository) -> None:
        super().__init__(repo)

    def create_team(self, class_id: int, name: str, principal_user_id: int | None) -> int:
        return self.repo.create_team(class_id, name, principal_user_id)

    def update_team_principal(self, team_id: int, principal_user_id: int | None) -> None:
        self.repo.update_team_principal(team_id, principal_user_id)

    def add_team_member(self, team_id: int, user_id: int, role: str = "Member") -> None:
        self.repo.add_team_member(team_id, user_id, role)

    def list_teams(self, class_id: int) -> list[dict]:
        return self.repo.list_teams(class_id)

    def list_team_members(self, team_id: int) -> list[dict]:
        return self.repo.list_team_members(team_id)

    def set_member_role(self, team_id: int, user_id: int, role: str) -> None:
        self.repo.set_member_role(team_id, user_id, role)

    def list_teams_for_user(self, user_id: int) -> list[dict]:
        return self.repo.list_teams_for_user(user_id)

    def update_team(self, team_id: int, name: str) -> None:
        self.repo.update_team(team_id, name)

    def delete_team(self, team_id: int) -> None:
        self.repo.delete_team(team_id)

    def list_all_teams(self) -> list[dict]:
        return self.repo.list_all_teams()

    def get_team(self, team_id: int) -> dict | None:
        return self.repo.get_team(team_id)

    def create_invitation(self, team_id: int, user_id: int) -> int:
        return self.repo.create_invitation(team_id, user_id, datetime.now(UTC).isoformat())

    def list_invitations_for_user(self, user_id: int) -> list[dict]:
        return self.repo.list_invitations_for_user(user_id)

    def accept_invitation(self, invitation_id: int) -> None:
        if not self.repo.accept_invitation(invitation_id):
            raise ValueError("Invitation not found")

    def decline_invitation(self, invitation_id: int) -> None:
        self.repo.set_invitation_status(invitation_id, "Declined")

    def list_invitations_for_team(self, team_id: int) -> list[dict]:
        return self.repo.list_invitations_for_team(team_id)
