from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable


# ---------- Domain models / DTOs ----------

@dataclass(frozen=True)
class User:
    user_id: str
    email: str
    password_hash: str
    is_active: bool = True


@dataclass(frozen=True)
class Session:
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class CreateUserCmd:
    email: str
    password: str


@dataclass(frozen=True)
class LoginCmd:
    email: str
    password: str


@dataclass(frozen=True)
class LogoutCmd:
    session_id: str


@dataclass(frozen=True)
class AuthResult:
    user_id: str
    session_id: str
    expires_at: datetime


# ---------- Errors ----------

class IdentityError(Exception):
    """Base error for identity use-cases."""


class UserAlreadyExists(IdentityError):
    pass


class UserNotFound(IdentityError):
    pass


class UserDisabled(IdentityError):
    pass


class InvalidCredentials(IdentityError):
    pass


class SessionNotFound(IdentityError):
    pass


# ---------- Ports (Protocols) ----------

@runtime_checkable
class UserRepository(Protocol):
    def get_by_email(self, email: str) -> User | None: ...
    def get_by_id(self, user_id: str) -> User | None: ...
    def create(self, user: User) -> None: ...


@runtime_checkable
class PasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...
    def verify_password(self, password: str, password_hash: str) -> bool: ...


@runtime_checkable
class SessionStore(Protocol):
    def create_session(self, session: Session) -> None: ...
    def get_session(self, session_id: str) -> Session | None: ...
    def delete_session(self, session_id: str) -> None: ...


@runtime_checkable
class IdGenerator(Protocol):
    def new_id(self) -> str: ...


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...


def default_session_ttl() -> timedelta:
    return timedelta(hours=12)
