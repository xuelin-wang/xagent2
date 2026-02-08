from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from xagent2.identity.core import IdentityConfig, IdentityService
from xagent2.identity_api.core import CreateUserCmd, InvalidCredentials, LoginCmd, SessionNotFound


class FixedClock:
    def __init__(self, now: datetime):
        self._now = now

    def now(self) -> datetime:
        return self._now


class FixedIds:
    def __init__(self):
        self._i = 0

    def new_id(self) -> str:
        self._i += 1
        return f"id-{self._i}"


class FakeHasher:
    def hash_password(self, password: str) -> str:
        return f"h:{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == f"h:{password}"


class MemUsers:
    def __init__(self):
        self.by_email = {}
        self.by_id = {}

    def get_by_email(self, email: str):
        return self.by_email.get(email)

    def get_by_id(self, user_id: str):
        return self.by_id.get(user_id)

    def create(self, user):
        self.by_email[user.email] = user
        self.by_id[user.user_id] = user


class MemSessions:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session):
        self.sessions[session.session_id] = session

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        self.sessions.pop(session_id, None)


def build_identity(now: datetime, ttl: timedelta = timedelta(hours=1)) -> IdentityService:
    return IdentityService(
        config=IdentityConfig(session_ttl=ttl),
        users=MemUsers(),
        sessions=MemSessions(),
        hasher=FakeHasher(),
        ids=FixedIds(),
        clock=FixedClock(now),
    )


def test_create_user_then_login_success():
    now = datetime(2026, 2, 8, tzinfo=timezone.utc)
    identity = build_identity(now)

    u = identity.create_user(CreateUserCmd(email="A@Example.com", password="pw"))
    assert u.email == "a@example.com"

    auth = identity.login(LoginCmd(email="a@example.com", password="pw"))
    assert auth.user_id == u.user_id
    assert auth.session_id.startswith("id-")


def test_login_wrong_password_fails():
    now = datetime(2026, 2, 8, tzinfo=timezone.utc)
    identity = build_identity(now)
    identity.create_user(CreateUserCmd(email="a@example.com", password="pw"))

    with pytest.raises(InvalidCredentials):
        identity.login(LoginCmd(email="a@example.com", password="nope"))


def test_session_expires_and_is_removed():
    now = datetime(2026, 2, 8, tzinfo=timezone.utc)
    identity = build_identity(now, ttl=timedelta(seconds=10))
    identity.create_user(CreateUserCmd(email="a@example.com", password="pw"))
    auth = identity.login(LoginCmd(email="a@example.com", password="pw"))

    identity._clock._now = now + timedelta(seconds=11)  # type: ignore[attr-defined]

    with pytest.raises(SessionNotFound):
        identity.authenticate_session(auth.session_id)
