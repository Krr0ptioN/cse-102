from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.repositories.auth_repository import AuthRepository
from app.core.services.base import Service


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    name: str
    email: str
    role: str


class AuthService(Service):
    MIN_PASSWORD_LENGTH = 8
    ALLOWED_ROLES = {"teacher", "student"}

    def __init__(self, repo: AuthRepository) -> None:
        super().__init__(repo)

    def sign_up(
        self, name: str, email: str, password: str, role: str
    ) -> AuthenticatedUser:
        self.log.info("Sign-up attempt for email=%s role=%s", email.strip().lower(), role)
        clean_name = name.strip()
        clean_email = self._normalize_email(email)
        clean_role = role.strip().lower()
        clean_password = password.strip()

        if not clean_name:
            raise ValueError("Name is required")
        if not clean_email:
            raise ValueError("Email is required")
        if clean_role not in self.ALLOWED_ROLES:
            raise ValueError("Role must be teacher or student")
        if len(clean_password) < self.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )

        password_hash, password_salt = self._hash_password(clean_password)
        now = datetime.now(UTC).isoformat()
        existing = self.repo.find_user_by_email(clean_email)

        if existing is not None:
            existing_hash = existing.get("password_hash")
            existing_role = (existing.get("role") or "").lower()
            if existing_hash:
                raise ValueError("An account with this email already exists")
            if existing_role and existing_role != clean_role:
                raise ValueError(
                    f"This email is reserved for a {existing_role} account"
                )
            self.repo.claim_existing_account(
                user_id=int(existing["id"]),
                name=clean_name,
                role=clean_role,
                password_hash=password_hash,
                password_salt=password_salt,
                created_at=now,
            )
            self.log.success("Existing account claimed for email=%s", clean_email)
            return self.require_user(int(existing["id"]))

        user_id = self.repo.create_account(
            name=clean_name,
            email=clean_email,
            role=clean_role,
            password_hash=password_hash,
            password_salt=password_salt,
            created_at=now,
        )
        self.log.success("User created id=%s email=%s role=%s", user_id, clean_email, clean_role)
        return self.require_user(user_id)

    def sign_in(self, email: str, password: str) -> AuthenticatedUser:
        clean_email = self._normalize_email(email)
        self.log.info("Sign-in attempt for email=%s", clean_email)
        if not clean_email or not password:
            raise ValueError("Email and password are required")

        user = self.repo.find_user_by_email(clean_email)
        if user is None:
            raise ValueError("Invalid email or password")
        if not bool(user.get("is_active", 1)):
            raise ValueError("This account is inactive")

        password_hash = user.get("password_hash")
        password_salt = user.get("password_salt")
        if not password_hash or not password_salt:
            raise ValueError("Invalid email or password")

        if not self._verify_password(password, password_salt, password_hash):
            raise ValueError("Invalid email or password")

        self.repo.set_last_login(int(user["id"]), datetime.now(UTC).isoformat())
        self.log.success("Sign-in success user_id=%s email=%s", int(user["id"]), clean_email)
        return self.require_user(int(user["id"]))

    def require_user(self, user_id: int) -> AuthenticatedUser:
        user = self.repo.find_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        return AuthenticatedUser(
            id=int(user["id"]),
            name=str(user["name"]),
            email=str(user["email"]),
            role=str(user["role"]).lower(),
        )

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _hash_password(self, password: str) -> tuple[str, str]:
        salt = os.urandom(16)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )
        return digest.hex(), salt.hex()

    def _verify_password(
        self, password: str, salt_hex: str, expected_hash_hex: str
    ) -> bool:
        try:
            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(expected_hash_hex)
        except ValueError:
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )
        return hmac.compare_digest(digest, expected_hash)
