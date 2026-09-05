from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.public import get_public_cache
from app.db.session import get_session
from app.fixtures.development import seed_development_content
from app.main import app
from app.models.content import JournalArticle, Project, PublicationState
from app.services.public_cache import TaggedPublicCache
from app.services.public_content import PublicContentService


class FakePipeline:
    def __init__(self, redis: FakeRedis) -> None:
        self.redis = redis
        self.operations: list[tuple[str, tuple[object, ...]]] = []

    def set(self, *args: object, **kwargs: object) -> FakePipeline:
        self.operations.append(("set", args))
        return self

    def sadd(self, *args: object) -> FakePipeline:
        self.operations.append(("sadd", args))
        return self

    def expire(self, *args: object) -> FakePipeline:
        return self

    def delete(self, *args: object) -> FakePipeline:
        self.operations.append(("delete", args))
        return self

    def execute(self) -> list[object]:
        for operation, args in self.operations:
            if operation == "set":
                self.redis.values[str(args[0])] = str(args[1])
            elif operation == "sadd":
                self.redis.tag_members.setdefault(str(args[0]), set()).add(str(args[1]))
            elif operation == "delete":
                self.redis.values.pop(str(args[0]), None)
                self.redis.tag_members.pop(str(args[0]), None)
        return []


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.tag_members: dict[str, set[str]] = {}

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def pipeline(self, *, transaction: bool) -> FakePipeline:
        assert transaction is False
        return FakePipeline(self)

    def sscan_iter(self, key: str, *, count: int) -> list[str]:
        assert count == 100
        return list(self.tag_members.get(key, set()))


def _draft_project() -> Project:
    return Project(
        slug="internal-draft",
        publication_state=PublicationState.DRAFT,
        display_order=99,
        featured=False,
        title_en="Internal draft",
        title_fa="پیش‌نویس داخلی",
        summary_en="Must never reach a public response.",
        summary_fa="هرگز نباید در پاسخ عمومی دیده شود.",
        location_en="Private",
        location_fa="خصوصی",
    )


def test_public_queries_exclude_drafts_and_internal_state(session: Session) -> None:
    session.add(_draft_project())
    category = session.scalar(select(JournalArticle.category_id).limit(1))
    assert category is not None
    session.add(
        JournalArticle(
            slug="internal-article",
            publication_state=PublicationState.DRAFT,
            category_id=category,
            title_en="Internal article",
            title_fa="مقالهٔ داخلی",
            excerpt_en="Must not leak.",
            excerpt_fa="نباید افشا شود.",
            body_en="Private body.",
            body_fa="بدنهٔ خصوصی.",
            reading_minutes=1,
        )
    )
    session.commit()

    service = PublicContentService(session)
    projects = service.projects("en")
    assert all(item.slug != "internal-draft" for item in projects.items)
    assert service.project("internal-draft", "en") is None
    assert service.article("internal-article", "fa") is None
    assert all(item.slug != "internal-draft" for item in service.search("en", "internal").items)

    public_project = projects.items[0].model_dump()
    assert "publication_state" not in public_project
    assert "created_at" not in public_project
    assert projects.items[0].title
    assert service.projects("fa").items[0].title
    project_detail = service.project("courtyard-house", "en")
    assert project_detail is not None
    assert len(project_detail.gallery) == 2


def test_tagged_cache_invalidates_only_known_tag_members() -> None:
    redis = FakeRedis()
    cache = TaggedPublicCache(redis)  # type: ignore[arg-type]
    calls = 0

    def home_payload() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"value": "home"}

    assert cache.get_or_set("v1:home:en", tags={"home", "home:en"}, factory=home_payload) == {
        "value": "home"
    }
    assert cache.get_or_set("v1:home:en", tags={"home", "home:en"}, factory=home_payload) == {
        "value": "home"
    }
    cache.get_or_set(
        "v1:article:one:en", tags={"article:one"}, factory=lambda: {"value": "article"}
    )
    assert calls == 1

    cache.invalidate({"home"})
    assert "voluma:cache:v1:home:en" not in redis.values
    assert "voluma:cache:v1:article:one:en" in redis.values
    cache.get_or_set("v1:home:en", tags={"home", "home:en"}, factory=home_payload)
    assert calls == 2


def test_public_route_excludes_draft_and_uses_response_schema(session: Session) -> None:
    session.add(_draft_project())
    session.commit()
    cache = TaggedPublicCache(FakeRedis())  # type: ignore[arg-type]
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_public_cache] = lambda: cache
    try:
        client = TestClient(app)
        list_response = client.get("/api/v1/public/projects?locale=en")
        assert list_response.status_code == 200
        payload = list_response.json()
        assert all(item["slug"] != "internal-draft" for item in payload["items"])
        assert "publication_state" not in payload["items"][0]

        draft_response = client.get("/api/v1/public/projects/internal-draft?locale=en")
        assert draft_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_development_fixture_is_idempotent(session: Session) -> None:
    assert PublicContentService(session).home("en") is not None
    assert seed_development_content(session) is False
