from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from xagent2.identity_api.core import (
    AuthResult,
    Clock,
    CreateUserCmd,
    IdGenerator,
    InvalidCredentials,
    LoginCmd,
    LogoutCmd,
    PasswordHasher,
    Session,
    SessionNotFound,
    SessionStore,
    User,
    UserAlreadyExists,
    UserDisabled,
    UserRepository,
    default_session_ttl,
)


@dataclass(frozen=True)
class IdentityConfig:
    session_ttl: timedelta = default_session_ttl()


class IdentityService:
    """
    Core identity use-cases (no FastAPI, no DB client imports).
    Depends only on ports from identity_api.
    """

    def __init__(
        self,
        *,
        config: IdentityConfig,
        users: UserRepository,
        sessions: SessionStore,
        hasher: PasswordHasher,
        ids: IdGenerator,
        clock: Clock,
    ) -> None:
        self._cfg = config
        self._users = users
        self._sessions = sessions
        self._hasher = hasher
        self._ids = ids
        self._clock = clock

    def create_user(self, cmd: CreateUserCmd) -> User:
        email = cmd.email.strip().lower()
        if not email:
            raise ValueError("email must not be empty")
        if not cmd.password:
            raise ValueError("password must not be empty")

        if self._users.get_by_email(email) is not None:
            raise UserAlreadyExists()

        user_id = self._ids.new_id()
        pw_hash = self._hasher.hash_password(cmd.password)
        user = User(user_id=user_id, email=email, password_hash=pw_hash, is_active=True)
        self._users.create(user)
        return user

    def login(self, cmd: LoginCmd) -> AuthResult:
        email = cmd.email.strip().lower()
        user = self._users.get_by_email(email)
        if user is None:
            raise InvalidCredentials()

        if not user.is_active:
            raise UserDisabled()

        if not self._hasher.verify_password(cmd.password, user.password_hash):
            raise InvalidCredentials()

        now = self._clock.now()
        session_id = self._ids.new_id()
        expires_at = now + self._cfg.session_ttl
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            created_at=now,
            expires_at=expires_at,
        )
        self._sessions.create_session(session)
        return AuthResult(user_id=user.user_id, session_id=session_id, expires_at=expires_at)

    def logout(self, cmd: LogoutCmd) -> None:
        sess = self._sessions.get_session(cmd.session_id)
        if sess is None:
            raise SessionNotFound()
        self._sessions.delete_session(cmd.session_id)

    def authenticate_session(self, session_id: str) -> str:
        """
        Helper used by inbound adapters: validates session and returns user_id.
        """
        sess = self._sessions.get_session(session_id)
        if sess is None:
            raise SessionNotFound()
        if self._clock.now() >= sess.expires_at:
            self._sessions.delete_session(session_id)
            raise SessionNotFound()
        return sess.user_id
