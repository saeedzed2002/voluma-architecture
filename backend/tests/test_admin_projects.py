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


@pytest.mark.parametrize("kind", ["expertise", "process"])
def test_editorial_content_workflow_drafts_validates_publishing_and_invalidates_cache(
    session: Session,
    client: tuple[TestClient, RecordingCache],
    kind: str,
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    draft = test_client.post(f"/api/v1/admin/{kind}", headers=headers, json={})
    assert draft.status_code == 201
    record_id = UUID(draft.json()["id"])
    assert draft.json()["publication_state"] == "draft"
    assert cache.invalidated == []

    invalid_publish = test_client.put(
        f"/api/v1/admin/{kind}/{record_id}",
        headers=headers,
        json={"publication_state": "published"},
    )
    assert invalid_publish.status_code == 422
    assert set(invalid_publish.json()["detail"]["fields"]) == {
        "title_en",
        "title_fa",
        "summary_en",
        "summary_fa",
    }

    published = test_client.put(
        f"/api/v1/admin/{kind}/{record_id}",
        headers=headers,
        json={
            "publication_state": "published",
            "title_en": f"Test {kind.title()}",
            "title_fa": f"آزمون {kind}",
            "summary_en": "A bilingual editorial entry managed through the administrator API.",
            "summary_fa": "یک مدخل تحریری دوزبانه که از مسیر ادمین مدیریت می‌شود.",
        },
    )
    assert published.status_code == 200
    assert published.json()["publication_state"] == "published"
    assert cache.invalidated[-1] >= {"home", kind, f"{kind}:en", f"{kind}:fa"}

    public = test_client.get(f"/api/v1/public/{kind}?locale=en")
    assert public.status_code == 200
    assert any(item["title"] == f"Test {kind.title()}" for item in public.json())

    listed = test_client.get(f"/api/v1/admin/{kind}")
    assert listed.status_code == 200
    identifiers = [item["id"] for item in listed.json()["items"]]
    incomplete = test_client.put(
        f"/api/v1/admin/{kind}/order", headers=headers, json={"identifiers": identifiers[:1]}
    )
    assert incomplete.status_code == 422

    reordered = test_client.put(
        f"/api/v1/admin/{kind}/order",
        headers=headers,
        json={"identifiers": list(reversed(identifiers))},
    )
    assert reordered.status_code == 200
    assert [item["display_order"] for item in reordered.json()["items"]] == list(
        range(len(identifiers))
    )

    deleted = test_client.delete(f"/api/v1/admin/{kind}/{record_id}", headers=headers)
    assert deleted.status_code == 204
    assert cache.invalidated[-1] >= {"home", kind}

    actions = session.scalars(
        select(AuditEvent.action)
        .where(AuditEvent.target_id == record_id)
        .order_by(AuditEvent.created_at)
    ).all()
    assert actions == [f"{kind}.created", f"{kind}.updated", f"{kind}.reordered", f"{kind}.deleted"]


def test_studio_people_workflow_publishes_to_the_public_response_and_audits_mutations(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    draft = test_client.post("/api/v1/admin/people", headers=headers, json={})
    assert draft.status_code == 201
    person_id = UUID(draft.json()["id"])
    assert draft.json()["publication_state"] == "draft"
    assert cache.invalidated == []

    invalid_publish = test_client.put(
        f"/api/v1/admin/people/{person_id}",
        headers=headers,
        json={"publication_state": "published"},
    )
    assert invalid_publish.status_code == 422
    assert set(invalid_publish.json()["detail"]["fields"]) == {"name", "role_en", "role_fa"}

    published = test_client.put(
        f"/api/v1/admin/people/{person_id}",
        headers=headers,
        json={
            "publication_state": "published",
            "name": "Test Studio Member",
            "role_en": "Architect",
            "role_fa": "معمار",
            "biography_en": "A public bilingual biography.",
            "biography_fa": "یک زندگی‌نامهٔ عمومی دوزبانه.",
        },
    )
    assert published.status_code == 200
    assert cache.invalidated[-1] >= {"home", "studio", "studio:en", "studio:fa"}

    public = test_client.get("/api/v1/public/studio?locale=en")
    assert public.status_code == 200
    assert any(member["name"] == "Test Studio Member" for member in public.json()["members"])

    second = test_client.post(
        "/api/v1/admin/people",
        headers=headers,
        json={
            "publication_state": "published",
            "name": "Second Studio Member",
            "role_en": "Designer",
            "role_fa": "طراح",
        },
    )
    assert second.status_code == 201
    reordered = test_client.put(
        "/api/v1/admin/people/order",
        headers=headers,
        json={"identifiers": [second.json()["id"], str(person_id)]},
    )
    assert reordered.status_code == 200
    assert [item["display_order"] for item in reordered.json()["items"]] == [0, 1]

    deleted = test_client.delete(f"/api/v1/admin/people/{person_id}", headers=headers)
    assert deleted.status_code == 204
    assert cache.invalidated[-1] >= {"home", "studio"}

    actions = session.scalars(
        select(AuditEvent.action)
        .where(AuditEvent.target_id == person_id)
        .order_by(AuditEvent.created_at)
    ).all()
    assert actions == ["people.created", "people.updated", "people.reordered", "people.deleted"]


def test_recognition_workflow_publishes_to_the_public_response_and_audits_mutations(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    draft = test_client.post("/api/v1/admin/recognition", headers=headers, json={})
    assert draft.status_code == 201
    recognition_id = UUID(draft.json()["id"])
    assert draft.json()["publication_state"] == "draft"
    assert cache.invalidated == []

    invalid_publish = test_client.put(
        f"/api/v1/admin/recognition/{recognition_id}",
        headers=headers,
        json={"publication_state": "published"},
    )
    assert invalid_publish.status_code == 422
    assert set(invalid_publish.json()["detail"]["fields"]) == {"title_en", "title_fa"}

    published = test_client.put(
        f"/api/v1/admin/recognition/{recognition_id}",
        headers=headers,
        json={
            "publication_state": "published",
            "title_en": "Test Recognition",
            "title_fa": "تقدیر آزمایشی",
        },
    )
    assert published.status_code == 200
    assert cache.invalidated[-1] >= {"home", "studio", "studio:en", "studio:fa"}

    public = test_client.get("/api/v1/public/studio?locale=en")
    assert public.status_code == 200
    assert "Test Recognition" in public.json()["recognitions"]

    second = test_client.post(
        "/api/v1/admin/recognition",
        headers=headers,
        json={
            "publication_state": "published",
            "title_en": "Second Recognition",
            "title_fa": "تقدیر دوم",
        },
    )
    assert second.status_code == 201
    reordered = test_client.put(
        "/api/v1/admin/recognition/order",
        headers=headers,
        json={"identifiers": [second.json()["id"], str(recognition_id)]},
    )
    assert reordered.status_code == 200
    assert [item["display_order"] for item in reordered.json()["items"]] == [0, 1]

    deleted = test_client.delete(f"/api/v1/admin/recognition/{recognition_id}", headers=headers)
    assert deleted.status_code == 204
    assert cache.invalidated[-1] >= {"home", "studio"}

    actions = session.scalars(
        select(AuditEvent.action)
        .where(AuditEvent.target_id == recognition_id)
        .order_by(AuditEvent.created_at)
    ).all()
    assert actions == [
        "recognition.created",
        "recognition.updated",
        "recognition.reordered",
        "recognition.deleted",
    ]


def test_journal_categories_and_articles_publish_bilingual_editorial_blocks(
    session: Session, client: tuple[TestClient, RecordingCache]
) -> None:
    test_client, cache = client
    _administrator(session)
    headers = _login(test_client)

    category = test_client.post(
        "/api/v1/admin/journal/categories",
        headers=headers,
        json={
            "slug": "material-culture",
            "title_en": "Material Culture",
            "title_fa": "فرهنگ مصالح",
        },
    )
    assert category.status_code == 201
    category_id = category.json()["id"]

    second_category = test_client.post(
        "/api/v1/admin/journal/categories",
        headers=headers,
        json={"slug": "field-notes", "title_en": "Field Notes", "title_fa": "یادداشت‌های میدانی"},
    )
    assert second_category.status_code == 201

    listed_categories = test_client.get("/api/v1/admin/journal/categories")
    assert listed_categories.status_code == 200
    identifiers = [item["id"] for item in listed_categories.json()["items"]]
    reordered_categories = test_client.put(
        "/api/v1/admin/journal/categories/order",
        headers=headers,
        json={"identifiers": list(reversed(identifiers))},
    )
    assert reordered_categories.status_code == 200
    assert [item["display_order"] for item in reordered_categories.json()["items"]] == list(
        range(len(identifiers))
    )

    draft = test_client.post(
        "/api/v1/admin/journal/articles",
        headers=headers,
        json={"slug": "measured-material", "category_id": category_id},
    )
    assert draft.status_code == 201
    article_id = UUID(draft.json()["id"])
    assert draft.json()["publication_state"] == "draft"

    invalid_publish = test_client.put(
        f"/api/v1/admin/journal/articles/{article_id}",
        headers=headers,
        json={
            "publication_state": "published",
            "category_id": category_id,
            "title_en": "Measured Material",
            "title_fa": "مصالح سنجیده",
            "excerpt_en": "An editorial test article.",
            "excerpt_fa": "یک یادداشت تحریری آزمایشی.",
            "blocks": [],
        },
    )
    assert invalid_publish.status_code == 422
    assert invalid_publish.json()["detail"]["fields"] == ["blocks"]

    published = test_client.put(
        f"/api/v1/admin/journal/articles/{article_id}",
        headers=headers,
        json={
            "publication_state": "published",
            "category_id": category_id,
            "title_en": "Measured Material",
            "title_fa": "مصالح سنجیده",
            "excerpt_en": "An editorial test article with bilingual structured blocks.",
            "excerpt_fa": "یک یادداشت آزمایشی با بلوک‌های ساخت‌یافتهٔ دوزبانه.",
            "reading_minutes": 4,
            "blocks": [
                {
                    "block_type": "text",
                    "content_en": {"heading": "Material", "body": "A measured English paragraph."},
                    "content_fa": {"heading": "مصالح", "body": "یک بند فارسی سنجیده."},
                },
                {
                    "block_type": "quote",
                    "content_en": {"quote": "Material records time.", "attribution": "VOLUMA"},
                    "content_fa": {"quote": "مصالح زمان را ثبت می‌کند.", "attribution": "ولوما"},
                },
            ],
        },
    )
    assert published.status_code == 200
    assert published.json()["published_at"] is not None
    assert len(published.json()["blocks"]) == 2
    assert cache.invalidated[-1] >= {
        "home",
        "journal-list",
        "article:measured-material",
        "article:measured-material:en",
        "article:measured-material:fa",
    }

    public = test_client.get("/api/v1/public/journal/measured-material?locale=fa")
    assert public.status_code == 200
    assert public.json()["seo_title"] == "مصالح سنجیده"
    assert public.json()["blocks"][0]["body"] == "یک بند فارسی سنجیده."
    assert public.json()["blocks"][1]["quote"] == "مصالح زمان را ثبت می‌کند."

    category_in_use = test_client.delete(
        f"/api/v1/admin/journal/categories/{category_id}", headers=headers
    )
    assert category_in_use.status_code == 409

    renamed_category = test_client.put(
        f"/api/v1/admin/journal/categories/{category_id}",
        headers=headers,
        json={
            "slug": "material-culture",
            "title_en": "Material Studies",
            "title_fa": "پژوهش مصالح",
        },
    )
    assert renamed_category.status_code == 200
    assert cache.invalidated[-1] >= {"journal-list", "article:measured-material"}

    deleted_article = test_client.delete(
        f"/api/v1/admin/journal/articles/{article_id}", headers=headers
    )
    assert deleted_article.status_code == 204
    deleted_category = test_client.delete(
        f"/api/v1/admin/journal/categories/{category_id}", headers=headers
    )
    assert deleted_category.status_code == 204

    actions = session.scalars(
        select(AuditEvent.action)
        .where(AuditEvent.target_id == article_id)
        .order_by(AuditEvent.created_at)
    ).all()
    assert actions == [
        "journal_article.created",
        "journal_article.updated",
        "journal_article.deleted",
    ]
