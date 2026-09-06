from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin import SESSION_COOKIE_NAME, get_admin_redis
from app.core.config import Settings
from app.db.session import get_session
from app.main import app
from app.models.admin import AdminUser, AuditEvent
from app.services.admin_auth import (
    InitialAdministratorConfigurationError,
    hash_password,
    provision_initial_administrator,
)

ORIGIN = "http://localhost:3000"
PASSWORD = "a test-only administrator password"


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if self.values.pop(key, None) is not None:
                deleted += 1
        return deleted

    def expire(self, key: str, ttl_seconds: int) -> bool:
        assert key in self.values
        assert ttl_seconds > 0
        return True

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def incr(self, key: str) -> int:
        value = int(self.values.get(key, "0")) + 1
        self.values[key] = str(value)
        return value

    def set(self, key: str, value: str, *, ex: int) -> bool:
        assert ex > 0
        self.values[key] = value
        return True


@pytest.fixture
def client(session: Session) -> Generator[tuple[TestClient, FakeRedis]]:
    redis = FakeRedis()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_admin_redis] = lambda: redis
    with TestClient(app) as test_client:
        yield test_client, redis
    app.dependency_overrides.clear()


def _administrator(session: Session) -> AdminUser:
    administrator = AdminUser(
        email="administrator@example.com",
        password_hash=hash_password(PASSWORD),
        is_active=True,
    )
    session.add(administrator)
    session.commit()
    return administrator


def _login(client: TestClient) -> tuple[dict[str, object], str]:
    response = client.post(
        "/api/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "administrator@example.com", "password": PASSWORD},
    )
    assert response.status_code == 200
    return response.json(), response.headers["set-cookie"]


def test_login_stores_only_a_hashed_opaque_session_and_protects_mutations(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, redis = client
    _administrator(session)

    response = test_client.post(
        "/api/v1/admin/auth/login",
        headers={"Origin": "https://attacker.example"},
        json={"email": "administrator@example.com", "password": PASSWORD},
    )
    assert response.status_code == 403

    payload, set_cookie_header = _login(test_client)
    session_token = test_client.cookies.get(SESSION_COOKIE_NAME)
    assert session_token is not None
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header
    assert all(session_token not in key for key in redis.values)
    assert all(
        key.startswith("voluma:session:") or key.startswith("voluma:rate:") for key in redis.values
    )

    session_response = test_client.get("/api/v1/admin/auth/me")
    assert session_response.status_code == 200
    assert session_response.json()["csrf_token"] == payload["csrf_token"]

    dashboard_response = test_client.get("/api/v1/admin/dashboard")
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["projects"]["published"] >= 1

    missing_csrf_response = test_client.post(
        "/api/v1/admin/auth/logout", headers={"Origin": ORIGIN}
    )
    assert missing_csrf_response.status_code == 403

    logout_response = test_client.post(
        "/api/v1/admin/auth/logout",
        headers={"Origin": ORIGIN, "X-VOLUMA-CSRF": str(payload["csrf_token"])},
    )
    assert logout_response.status_code == 204
    assert test_client.get("/api/v1/admin/auth/me").status_code == 401


def test_login_errors_are_generic_and_rate_limited(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, _ = client
    _administrator(session)
    headers = {"Origin": ORIGIN}
    payload = {"email": "administrator@example.com", "password": "incorrect password"}

    for _ in range(5):
        response = test_client.post("/api/v1/admin/auth/login", headers=headers, json=payload)
        assert response.status_code == 401
        assert response.json() == {"detail": "invalid credentials"}

    response = test_client.post("/api/v1/admin/auth/login", headers=headers, json=payload)
    assert response.status_code == 429
    assert response.json() == {"detail": "try again later"}


def test_login_rotates_an_existing_session(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, redis = client
    _administrator(session)

    _login(test_client)
    first_token = test_client.cookies.get(SESSION_COOKIE_NAME)
    assert first_token is not None
    first_session_key = next(key for key in redis.values if key.startswith("voluma:session:"))
    _login(test_client)
    second_token = test_client.cookies.get(SESSION_COOKIE_NAME)

    assert second_token is not None
    assert second_token != first_token
    assert first_session_key not in redis.values


def test_initial_administrator_provisioning_is_idempotent_and_audited(session: Session) -> None:
    settings = Settings(
        VOLUMA_INITIAL_ADMIN_EMAIL="first-administrator@example.com",
        VOLUMA_INITIAL_ADMIN_PASSWORD=PASSWORD,
    )

    first = provision_initial_administrator(session, settings)
    session.commit()
    second = provision_initial_administrator(session, settings)

    assert first.id == second.id
    assert PASSWORD not in first.password_hash
    audit_events = session.scalars(select(AuditEvent).where(AuditEvent.actor_id == first.id)).all()
    assert [event.action for event in audit_events] == ["administrator.provisioned"]


def test_initial_administrator_provisioning_rejects_an_unusable_email(session: Session) -> None:
    settings = Settings(
        VOLUMA_INITIAL_ADMIN_EMAIL="administrator@voluma.invalid",
        VOLUMA_INITIAL_ADMIN_PASSWORD=PASSWORD,
    )

    with pytest.raises(InitialAdministratorConfigurationError) as error:
        provision_initial_administrator(session, settings)

    assert str(error.value) == "initial administrator email is invalid"
