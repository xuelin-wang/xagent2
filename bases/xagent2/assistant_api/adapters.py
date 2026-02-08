from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict

from xagent2.identity_api.core import (
    Clock,
    IdGenerator,
    PasswordHasher,
    Session,
    SessionStore,
    User,
    UserRepository,
)


class UuidLikeIdGenerator(IdGenerator):
    def new_id(self) -> str:
        # Opaque session IDs: use urlsafe tokens for easy cookie/header transport.
        return secrets.token_urlsafe(32)


class UtcClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class SimplePasswordHasher(PasswordHasher):
    """
    Dummy hasher for skeleton/testing.
    Replace with argon2/bcrypt in a real adapter component.
    """

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        return self.hash_password(password) == password_hash


class InMemoryUserRepo(UserRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return self._by_email.get(email)

    def get_by_id(self, user_id: str) -> User | None:
        return self._by_id.get(user_id)

    def create(self, user: User) -> None:
        self._by_id[user.user_id] = user
        self._by_email[user.email] = user


class InMemorySessionStore(SessionStore):
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def create_session(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
