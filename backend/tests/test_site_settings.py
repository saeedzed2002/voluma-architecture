from __future__ import annotations

from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin import get_admin_redis
from app.api.public import get_public_cache
from app.db.session import get_session
from app.main import app
from app.models.admin import AdminUser, AuditEvent
from app.models.content import SiteSettings
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

    def expire(self, _key: str, _ttl_seconds: int) -> bool:
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


class RecordingCache:
    def __init__(self) -> None:
        self.invalidated: list[set[str]] = []

    def invalidate(self, tags: set[str]) -> None:
        self.invalidated.append(tags)

    def get_or_set(self, _key: str, *, tags: set[str], factory: Callable[[], object]) -> object:
        return factory()


@pytest.fixture
def client(session: Session) -> Generator[tuple[TestClient, RecordingCache]]:
    redis = FakeRedis()
    cache = RecordingCache()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_admin_redis] = lambda: redis
    app.dependency_overrides[get_public_cache] = lambda: cache
    with TestClient(app) as test_client:
        yield test_client, cache
    app.dependency_overrides.clear()


def _login(session: Session, test_client: TestClient) -> dict[str, str]:
    session.add(
        AdminUser(
            email="administrator@example.com",
            password_hash=hash_password(PASSWORD),
            is_active=True,
        )
    )
    session.commit()
    response = test_client.post(
        "/api/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "administrator@example.com", "password": PASSWORD},
    )
    assert response.status_code == 200
    return {"Origin": ORIGIN, "X-VOLUMA-CSRF": response.json()["csrf_token"]}


def _settings_payload(test_client: TestClient) -> dict[str, object]:
    response = test_client.get("/api/v1/admin/settings")
    assert response.status_code == 200
    payload = response.json()
    payload.pop("id")
    payload.pop("updated_at")
    return payload


def test_settings_are_authenticated_csrf_protected_and_invalidate_public_content(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    assert test_client.get("/api/v1/admin/settings").status_code == 401
    headers = _login(session, test_client)
    payload = _settings_payload(test_client)
    payload.update(
        {
            "studio_name": "Measured Studio",
            "contact_email": "studio@example.com",
            "contact_phone": "+98 21 5555 0101",
            "contact_address_en": "Tehran, Iran",
            "contact_address_fa": "تهران، ایران",
            "social_links": [{"label": "Instagram", "url": "https://instagram.com/voluma"}],
            "default_theme": "dark",
            "default_seo_title_en": "Measured Studio — Architecture",
            "default_seo_title_fa": "استودیوی سنجیده — معماری",
            "default_seo_description_en": "Owner-managed architecture metadata.",
            "default_seo_description_fa": "فرادادهٔ معماریِ مدیریت‌شده توسط مالک.",
        }
    )

    assert test_client.put("/api/v1/admin/settings", json=payload).status_code == 403
    invalid = dict(payload)
    invalid["social_links"] = [{"label": "Unsafe", "url": "http://example.com"}]
    assert (
        test_client.put("/api/v1/admin/settings", headers=headers, json=invalid).status_code == 422
    )

    updated = test_client.put("/api/v1/admin/settings", headers=headers, json=payload)
    assert updated.status_code == 200
    assert updated.json()["contact_email"] == "studio@example.com"
    assert updated.json()["default_theme"] == "dark"
    assert cache.invalidated[-1] >= {"site", "site:en", "home", "studio:fa"}

    public = test_client.get("/api/v1/public/site?locale=fa")
    assert public.status_code == 200
    assert public.json() == {
        "studio_name": "Measured Studio",
        "logo_url": None,
        "favicon_url": None,
        "contact_email": "studio@example.com",
        "contact_phone": "+98 21 5555 0101",
        "contact_address": "تهران، ایران",
        "social_links": [{"label": "Instagram", "url": "https://instagram.com/voluma"}],
        "default_theme": "dark",
        "seo_title": "استودیوی سنجیده — معماری",
        "seo_description": "فرادادهٔ معماریِ مدیریت‌شده توسط مالک.",
        "privacy": session.scalar(select(SiteSettings.privacy_fa)),
    }
    actions = session.scalars(
        select(AuditEvent.action).where(AuditEvent.target_type == "site_settings")
    ).all()
    assert actions == ["site_settings.updated"]


def test_settings_update_bootstraps_the_singleton_when_no_record_exists(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, _cache = client
    existing = session.scalar(select(SiteSettings))
    assert existing is not None
    session.delete(existing)
    session.commit()
    headers = _login(session, test_client)
    draft = _settings_payload(test_client)
    created = test_client.put("/api/v1/admin/settings", headers=headers, json=draft)
    assert created.status_code == 200
    assert created.json()["id"] is not None
    assert session.scalar(select(SiteSettings)) is not None
