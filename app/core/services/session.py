from __future__ import annotations

from .base import Service
from .auth import AuthenticatedUser


class SessionService(Service):
    def __init__(self) -> None:
        # Session service is transient and doesn't need a repository
        # but we call super for logger consistency
        super().__init__(None)
        self._current_user: AuthenticatedUser | None = None

    def start(self, user: AuthenticatedUser) -> None:
        self._current_user = user

    def clear(self) -> None:
        self._current_user = None

    def current_user(self) -> AuthenticatedUser | None:
        return self._current_user

    def require_user(self) -> AuthenticatedUser:
        if self._current_user is None:
            raise ValueError("No active session")
        return self._current_user
