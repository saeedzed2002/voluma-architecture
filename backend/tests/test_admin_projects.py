from __future__ import annotations

from collections.abc import Callable, Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin import get_admin_redis
from app.api.public import get_public_cache
from app.db.session import get_session
from app.main import app
from app.models.admin import AdminUser, AuditEvent
from app.models.content import Discipline, Project, Typology
from app.services.admin_auth import hash_password

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


class RecordingCache:
    def __init__(self) -> None:
        self.invalidated: list[set[str]] = []

    def invalidate(self, tags: set[str]) -> None:
        self.invalidated.append(tags)

    def get_or_set(self, key: str, *, tags: set[str], factory: Callable[[], object]) -> object:
        return factory()


@pytest.fixture
def client(session: Session) -> Generator[tuple[TestClient, RecordingCache]]:
    cache = RecordingCache()
    redis = FakeRedis()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_admin_redis] = lambda: redis
    app.dependency_overrides[get_public_cache] = lambda: cache
    with TestClient(app) as test_client:
        yield test_client, cache
    app.dependency_overrides.clear()


def _administrator(session: Session) -> None:
    session.add(
        AdminUser(
            email="administrator@example.com",
            password_hash=hash_password(PASSWORD),
            is_active=True,
        )
    )
    session.commit()


def _login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "administrator@example.com", "password": PASSWORD},
    )
    assert response.status_code == 200
    return {"Origin": ORIGIN, "X-VOLUMA-CSRF": response.json()["csrf_token"]}


def _project_payload(session: Session, *, state: str = "draft") -> dict[str, object]:
    discipline_id = session.scalar(select(Discipline.id).order_by(Discipline.display_order))
    typology_id = session.scalar(select(Typology.id).order_by(Typology.display_order))
    assert discipline_id is not None and typology_id is not None
    return {
        "slug": "measured-courtyard",
        "publication_state": state,
        "featured": True,
        "title_en": "Measured Courtyard",
        "title_fa": "حیاط سنجیده",
        "summary_en": "A bilingual test project with complete public editorial essentials.",
        "summary_fa": "یک پروژهٔ آزمایشی دوزبانه با اطلاعات کامل عمومی.",
        "location_en": "Tehran",
        "location_fa": "تهران",
        "discipline_ids": [str(discipline_id)],
        "typology_ids": [str(typology_id)],
    }


def _without_slug(payload: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if key != "slug"}


def test_project_workflow_keeps_drafts_private_and_invalidates_after_publish(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    form_options = test_client.get("/api/v1/admin/projects/form-options")
    assert form_options.status_code == 200
    assert form_options.json()["disciplines"]
    assert form_options.json()["typologies"]

    created = test_client.post(
        "/api/v1/admin/projects", headers=headers, json=_project_payload(session)
    )
    assert created.status_code == 201
    project_id = UUID(created.json()["id"])
    assert created.json()["publication_state"] == "draft"
    assert cache.invalidated == []

    public = test_client.get("/api/v1/public/projects/measured-courtyard?locale=en")
    assert public.status_code == 404

    published_payload = _without_slug(_project_payload(session, state="published"))
    published = test_client.put(
        f"/api/v1/admin/projects/{project_id}", headers=headers, json=published_payload
    )
    assert published.status_code == 200
    assert published.json()["publication_state"] == "published"
    assert published.json()["published_at"] is not None
    assert "project:measured-courtyard" in cache.invalidated[-1]
    assert "project-list:fa" in cache.invalidated[-1]

    blocks = test_client.put(
        f"/api/v1/admin/projects/{project_id}/blocks",
        headers=headers,
        json={
            "blocks": [
                {
                    "block_type": "text",
                    "content_en": {"heading": "Approach", "body": "Measured light and shade."},
                    "content_fa": {"heading": "رویکرد", "body": "نور و سایهٔ سنجیده."},
                },
                {
                    "block_type": "quote",
                    "content_en": {"quote": "Material should clarify the plan."},
                    "content_fa": {"quote": "مصالح باید پلان را روشن کنند."},
                },
            ]
        },
    )
    assert blocks.status_code == 200
    assert [block["display_order"] for block in blocks.json()["blocks"]] == [0, 1]
    assert cache.invalidated[-1] >= {"home", "project-list", "project:measured-courtyard"}

    invalid_block = test_client.put(
        f"/api/v1/admin/projects/{project_id}/blocks",
        headers=headers,
        json={
            "blocks": [
                {
                    "block_type": "text",
                    "content_en": {"body": "Safe content", "raw_html": "<script>alert(1)</script>"},
                    "content_fa": {"body": "محتوای ایمن"},
                }
            ]
        },
    )
    assert invalid_block.status_code == 422

    unpublished = test_client.put(
        f"/api/v1/admin/projects/{project_id}",
        headers=headers,
        json=_without_slug(_project_payload(session)),
    )
    assert unpublished.status_code == 200
    assert unpublished.json()["publication_state"] == "draft"
    assert cache.invalidated[-1] >= {"home", "project-list", "project:measured-courtyard"}
    assert (
        test_client.get("/api/v1/public/projects/measured-courtyard?locale=en").status_code == 404
    )

    actions = session.scalars(
        select(AuditEvent.action)
        .where(AuditEvent.target_id == project_id)
        .order_by(AuditEvent.created_at)
    ).all()
    assert actions == [
        "project.created",
        "project.updated",
        "project.blocks_replaced",
        "project.updated",
    ]


def test_project_order_requires_the_complete_collection_and_uses_unique_positions(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)
    listed = test_client.get("/api/v1/admin/projects")
    assert listed.status_code == 200
    identifiers = [item["id"] for item in listed.json()["items"]]
    assert len(identifiers) >= 2

    incomplete = test_client.put(
        "/api/v1/admin/projects/order", headers=headers, json={"project_ids": identifiers[:1]}
    )
    assert incomplete.status_code == 422

    reordered = test_client.put(
        "/api/v1/admin/projects/order",
        headers=headers,
        json={"project_ids": list(reversed(identifiers))},
    )
    assert reordered.status_code == 200
    items = reordered.json()["items"]
    assert [item["id"] for item in items] == list(reversed(identifiers))
    assert [item["display_order"] for item in items] == list(range(len(items)))
    assert cache.invalidated[-1] >= {"home", "project-list"}

    persisted = session.scalars(select(Project).order_by(Project.display_order)).all()
    assert [project.display_order for project in persisted] == list(range(len(persisted)))


def test_project_slug_is_immutable_after_creation(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, _ = client
    _administrator(session)
    headers = _login(test_client)
    created = test_client.post(
        "/api/v1/admin/projects", headers=headers, json=_project_payload(session)
    )
    assert created.status_code == 201
    changed_slug = _without_slug(_project_payload(session))
    changed_slug["slug"] = "a-different-slug"
    response = test_client.put(
        f"/api/v1/admin/projects/{created.json()['id']}", headers=headers, json=changed_slug
    )
    assert response.status_code == 422


def test_taxonomy_workflow_prevents_deleting_referenced_records_and_invalidates_projects(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    listed = test_client.get("/api/v1/admin/disciplines")
    assert listed.status_code == 200
    disciplines = listed.json()["items"]
    assert len(disciplines) >= 2
    referenced = disciplines[0]

    reordered = test_client.put(
        "/api/v1/admin/disciplines/order",
        headers=headers,
        json={"identifiers": [item["id"] for item in reversed(disciplines)]},
    )
    assert reordered.status_code == 200
    assert [item["display_order"] for item in reordered.json()["items"]] == list(
        range(len(disciplines))
    )
    assert cache.invalidated[-1] >= {"home", "project-list"}

    updated = test_client.put(
        f"/api/v1/admin/disciplines/{referenced['id']}",
        headers=headers,
        json={
            "slug": referenced["slug"],
            "title_en": "Updated discipline",
            "title_fa": "رشتهٔ به‌روزشده",
        },
    )
    assert updated.status_code == 200
    assert "project-list:en" in cache.invalidated[-1]

    in_use = test_client.delete(f"/api/v1/admin/disciplines/{referenced['id']}", headers=headers)
    assert in_use.status_code == 409

    created = test_client.post(
        "/api/v1/admin/disciplines",
        headers=headers,
        json={"slug": "temporary-discipline", "title_en": "Temporary", "title_fa": "موقت"},
    )
    assert created.status_code == 201
    deleted = test_client.delete(
        f"/api/v1/admin/disciplines/{created.json()['id']}", headers=headers
    )
    assert deleted.status_code == 204
