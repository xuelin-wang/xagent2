from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, EmailStr

from xagent2.identity_api.core import (
    CreateUserCmd,
    InvalidCredentials,
    LoginCmd,
    LogoutCmd,
    SessionNotFound,
    UserAlreadyExists,
    UserDisabled,
)
from xagent2.query_service.core import Query
from .wiring import Container, build_container


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    session_id: str
    expires_at: str


class MeResponse(BaseModel):
    user_id: str


class QueryRequest(BaseModel):
    text: str


class QueryResponse(BaseModel):
    answer: str
    created_at: str


def create_app() -> FastAPI:
    app = FastAPI(title="User API")
    container = build_container()

    def get_container() -> Container:
        return container

    def get_identity(container: Container = Depends(get_container)):
        return container.identity

    def get_answer_query(container: Container = Depends(get_container)):
        return container.answer_query

    def get_session_id(
        x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
    ) -> str:
        if not x_session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Session-Id",
            )
        return x_session_id

    @app.post("/users", status_code=status.HTTP_201_CREATED)
    def create_user(req: CreateUserRequest, identity=Depends(get_identity)):
        try:
            user = identity.create_user(CreateUserCmd(email=req.email, password=req.password))
            return {"user_id": user.user_id, "email": user.email}
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

    @app.post("/login", response_model=LoginResponse)
    def login(req: LoginRequest, identity=Depends(get_identity)):
        try:
            result = identity.login(LoginCmd(email=req.email, password=req.password))
            return LoginResponse(
                user_id=result.user_id,
                session_id=result.session_id,
                expires_at=result.expires_at.isoformat(),
            )
        except (InvalidCredentials, UserDisabled):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

    @app.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    def logout(session_id: str = Depends(get_session_id), identity=Depends(get_identity)):
        try:
            identity.logout(LogoutCmd(session_id=session_id))
            return None
        except SessionNotFound:
            return None

    @app.get("/me", response_model=MeResponse)
    def me(session_id: str = Depends(get_session_id), identity=Depends(get_identity)):
        try:
            user_id = identity.authenticate_session(session_id)
            return MeResponse(user_id=user_id)
        except SessionNotFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )

    @app.post("/query", response_model=QueryResponse)
    def query(
        req: QueryRequest,
        session_id: str = Depends(get_session_id),
        identity=Depends(get_identity),
        answer_query=Depends(get_answer_query),
    ):
        """
        Dummy endpoint that validates session and returns a simple answer.
        """
        try:
            identity.authenticate_session(session_id)
        except SessionNotFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )
        result = answer_query(Query(text=req.text))
        return QueryResponse(answer=result.text, created_at=result.created_at.isoformat())

    return app
