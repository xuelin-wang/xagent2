from __future__ import annotations

from fastapi.testclient import TestClient

from xagent2.assistant_api.core import create_app


def test_happy_path_create_login_me_logout():
    app = create_app()
    client = TestClient(app)

    r = client.post("/users", json={"email": "a@example.com", "password": "pw"})
    assert r.status_code == 201
    user_id = r.json()["user_id"]

    r = client.post("/login", json={"email": "a@example.com", "password": "pw"})
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == user_id
    session_id = body["session_id"]

    r = client.get("/me", headers={"X-Session-Id": session_id})
    assert r.status_code == 200
    assert r.json()["user_id"] == user_id

    r = client.post("/logout", headers={"X-Session-Id": session_id})
    assert r.status_code == 204

    r = client.get("/me", headers={"X-Session-Id": session_id})
    assert r.status_code == 401


def test_login_wrong_password_unauthorized():
    app = create_app()
    client = TestClient(app)

    client.post("/users", json={"email": "a@example.com", "password": "pw"})
    r = client.post("/login", json={"email": "a@example.com", "password": "nope"})
    assert r.status_code == 401


def test_query_requires_session_and_returns_answer():
    app = create_app()
    client = TestClient(app)

    client.post("/users", json={"email": "a@example.com", "password": "pw"})
    login = client.post("/login", json={"email": "a@example.com", "password": "pw"})
    session_id = login.json()["session_id"]

    r = client.post("/query", json={"text": "hello"}, headers={"X-Session-Id": session_id})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"].startswith("Echo:")
