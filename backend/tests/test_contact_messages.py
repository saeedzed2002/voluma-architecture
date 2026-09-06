from __future__ import annotations

import time
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin import SESSION_COOKIE_NAME, get_admin_redis
from app.db.session import get_session
from app.main import app
from app.models.admin import AdminUser, AuditEvent
from app.models.content import ContactMessage, ContactMessageState
from app.services.admin_auth import hash_password

ORIGIN = "http://localhost:3000"
PASSWORD = "a test-only administrator password"


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def delete(self, *keys: str) -> int:
        for key in keys:
            self.values.pop(key, None)
        return len(keys)

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


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "company": "Measured Studio",
        "email": "visitor@example.com",
        "message": "We would like to discuss an adaptive reuse project with a quiet public edge.",
        "name": "Preview visitor",
        "phone": "+98 21 5555 0101",
        "project_type": "reuse",
        "source_locale": "en",
        "started_at": int(time.time() * 1_000) - 5_000,
        "website": "",
    }
    payload.update(overrides)
    return payload


def _administrator(session: Session) -> AdminUser:
    administrator = AdminUser(
        email="administrator@example.com",
        password_hash=hash_password(PASSWORD),
        is_active=True,
    )
    session.add(administrator)
    session.commit()
    return administrator


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "administrator@example.com", "password": PASSWORD},
    )
    assert response.status_code == 200
    assert client.cookies.get(SESSION_COOKIE_NAME) is not None
    return str(response.json()["csrf_token"])


def test_contact_submission_validates_and_stores_no_request_metadata_body_in_redis(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, redis = client
    response = test_client.post("/api/v1/contact", json=_payload())

    assert response.status_code == 202
    assert response.json() == {"accepted": True}
    message = session.scalar(
        select(ContactMessage).where(ContactMessage.email == "visitor@example.com")
    )
    assert message is not None
    assert message.state == ContactMessageState.NEW
    assert message.body.startswith("We would like")
    assert all("We would like" not in value for value in redis.values.values())
    assert all(key.startswith("voluma:rate:contact:ip:") for key in redis.values)

    too_fast = test_client.post(
        "/api/v1/contact", json=_payload(started_at=int(time.time() * 1_000))
    )
    assert too_fast.status_code == 422

    honeytrap = test_client.post(
        "/api/v1/contact", json=_payload(email="bot@example.com", website="https://bot.invalid")
    )
    assert honeytrap.status_code == 202
    assert (
        session.scalar(select(ContactMessage).where(ContactMessage.email == "bot@example.com"))
        is None
    )


def test_contact_submission_is_rate_limited(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, _ = client
    for index in range(5):
        response = test_client.post(
            "/api/v1/contact", json=_payload(email=f"visitor{index}@example.com")
        )
        assert response.status_code == 202

    response = test_client.post("/api/v1/contact", json=_payload(email="limited@example.com"))
    assert response.status_code == 429
    assert response.json() == {"detail": "try again later"}


def test_administrator_can_triage_and_delete_contact_messages(
    session: Session, client: tuple[TestClient, FakeRedis]
) -> None:
    test_client, _ = client
    _administrator(session)
    created = test_client.post("/api/v1/contact", json=_payload())
    assert created.status_code == 202
    message = session.scalar(
        select(ContactMessage).where(ContactMessage.email == "visitor@example.com")
    )
    assert message is not None
    csrf_token = _login(test_client)

    listed = test_client.get("/api/v1/admin/messages?state=new")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["body"] == message.body

    updated = test_client.patch(
        f"/api/v1/admin/messages/{message.id}",
        headers={"Origin": ORIGIN, "X-VOLUMA-CSRF": csrf_token},
        json={"state": "archived"},
    )
    assert updated.status_code == 200
    assert updated.json()["state"] == "archived"
    assert updated.json()["archived_at"] is not None

    deleted = test_client.delete(
        f"/api/v1/admin/messages/{message.id}",
        headers={"Origin": ORIGIN, "X-VOLUMA-CSRF": csrf_token},
    )
    assert deleted.status_code == 204
    assert session.get(ContactMessage, message.id) is None
    events = session.scalars(select(AuditEvent).where(AuditEvent.target_id == message.id)).all()
    assert [event.action for event in events] == [
        "contact_message.state_updated",
        "contact_message.deleted",
    ]
