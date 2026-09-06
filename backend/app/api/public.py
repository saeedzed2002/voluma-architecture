from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from typing import Annotated, NoReturn, cast
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from redis import Redis

from app.core.config import get_settings
from app.db.session import SessionDep
from app.schemas.public import (
    ExpertiseResponse,
    HomeResponse,
    JournalArticleResponse,
    JournalListResponse,
    Locale,
    ProcessStepResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    SearchResponse,
    SiteResponse,
    StudioResponse,
)
from app.services.public_cache import TaggedPublicCache
from app.services.public_content import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT, PublicContentService

router = APIRouter(tags=["public"])
PUBLIC_RESPONSE_CACHE_VERSION = "v5"

LocaleQuery = Annotated[Locale, Query(description="Response locale.")]
PageLimit = Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)]
PageOffset = Annotated[int, Query(ge=0)]


@lru_cache
def _redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def get_public_cache() -> TaggedPublicCache:
    return TaggedPublicCache(_redis_client())


PublicCacheDep = Annotated[TaggedPublicCache, Depends(get_public_cache)]


def _cached[T](
    cache: TaggedPublicCache,
    *,
    key: str,
    tags: set[str],
    factory: Callable[[], object],
    parser: Callable[[object], T],
) -> T:
    value = cache.get_or_set(
        key,
        tags=tags,
        factory=lambda: _json_value(factory()),
    )
    return parser(value)


def _json_value(value: object) -> object:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    raise TypeError("public cache payload must be a response schema")


def _parse_model_list[T](value: object, parser: Callable[[object], T]) -> list[T]:
    return [parser(item) for item in cast(list[object], value)]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")


def _locale_tags(*families: str, locale: Locale) -> set[str]:
    return {tag for family in families for tag in (family, f"{family}:{locale}")}


def _query_cache_key(namespace: str, parameters: dict[str, str | int | None]) -> str:
    encoded = urlencode({key: value for key, value in parameters.items() if value is not None})
    return f"{namespace}?{encoded}"


def _cache_namespace(name: str) -> str:
    """Version cached response shapes so a deployment cannot deserialize stale payloads."""

    return f"{PUBLIC_RESPONSE_CACHE_VERSION}:{name}"


@router.get("/site", response_model=SiteResponse)
def site(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> SiteResponse:
    service = PublicContentService(session)
    response = _cached(
        cache,
        key=f"{_cache_namespace('site')}:{locale}",
        tags=_locale_tags("site", locale=locale),
        factory=lambda: service.site(locale) or (_raise_not_found()),
        parser=SiteResponse.model_validate,
    )
    return response


@router.get("/home", response_model=HomeResponse)
def home(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> HomeResponse:
    service = PublicContentService(session)
    response = _cached(
        cache,
        key=f"{_cache_namespace('home')}:{locale}",
        tags=_locale_tags(
            "home", "site", "project-list", "expertise", "process", "journal-list", locale=locale
        ),
        factory=lambda: service.home(locale) or (_raise_not_found()),
        parser=HomeResponse.model_validate,
    )
    return response


@router.get("/projects", response_model=ProjectListResponse)
def projects(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
    limit: PageLimit = DEFAULT_PAGE_LIMIT,
    offset: PageOffset = 0,
    q: Annotated[str | None, Query(max_length=120)] = None,
    discipline: Annotated[str | None, Query(max_length=80)] = None,
    typology: Annotated[str | None, Query(max_length=80)] = None,
    project_status: Annotated[str | None, Query(alias="status", max_length=100)] = None,
    location: Annotated[str | None, Query(max_length=160)] = None,
    year: int | None = None,
) -> ProjectListResponse:
    service = PublicContentService(session)
    parameters = {
        "locale": locale,
        "limit": limit,
        "offset": offset,
        "q": q,
        "discipline": discipline,
        "typology": typology,
        "status": project_status,
        "location": location,
        "year": year,
    }
    return _cached(
        cache,
        key=_query_cache_key(_cache_namespace("projects"), parameters),
        tags=_locale_tags("project-list", locale=locale),
        factory=lambda: service.projects(
            locale,
            limit=limit,
            offset=offset,
            query=q,
            discipline=discipline,
            typology=typology,
            status=project_status,
            location=location,
            year=year,
        ),
        parser=ProjectListResponse.model_validate,
    )


@router.get("/projects/{slug}", response_model=ProjectDetailResponse)
def project(
    slug: str,
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> ProjectDetailResponse:
    service = PublicContentService(session)
    return _cached(
        cache,
        key=f"{_cache_namespace(f'project:{slug}')}:{locale}",
        tags=_locale_tags(f"project:{slug}", "project-list", locale=locale),
        factory=lambda: service.project(slug, locale) or (_raise_not_found()),
        parser=ProjectDetailResponse.model_validate,
    )


@router.get("/expertise", response_model=list[ExpertiseResponse])
def expertise(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> list[ExpertiseResponse]:
    service = PublicContentService(session)
    return _cached(
        cache,
        key=f"{_cache_namespace('expertise')}:{locale}",
        tags=_locale_tags("expertise", locale=locale),
        factory=lambda: service.expertise(locale),
        parser=lambda value: _parse_model_list(value, ExpertiseResponse.model_validate),
    )


@router.get("/process", response_model=list[ProcessStepResponse])
def process(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> list[ProcessStepResponse]:
    service = PublicContentService(session)
    return _cached(
        cache,
        key=f"{_cache_namespace('process')}:{locale}",
        tags=_locale_tags("process", locale=locale),
        factory=lambda: service.process(locale),
        parser=lambda value: _parse_model_list(value, ProcessStepResponse.model_validate),
    )


@router.get("/studio", response_model=StudioResponse)
def studio(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> StudioResponse:
    service = PublicContentService(session)
    return _cached(
        cache,
        key=f"{_cache_namespace('studio')}:{locale}",
        tags=_locale_tags("studio", "site", locale=locale),
        factory=lambda: service.studio(locale) or (_raise_not_found()),
        parser=StudioResponse.model_validate,
    )


@router.get("/journal", response_model=JournalListResponse)
def journal(
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
    limit: PageLimit = DEFAULT_PAGE_LIMIT,
    offset: PageOffset = 0,
    category: Annotated[str | None, Query(max_length=80)] = None,
) -> JournalListResponse:
    service = PublicContentService(session)
    parameters = {"locale": locale, "limit": limit, "offset": offset, "category": category}
    return _cached(
        cache,
        key=_query_cache_key(_cache_namespace("journal"), parameters),
        tags=_locale_tags("journal-list", locale=locale),
        factory=lambda: service.journal(locale, limit=limit, offset=offset, category=category),
        parser=JournalListResponse.model_validate,
    )


@router.get("/journal/{slug}", response_model=JournalArticleResponse)
def article(
    slug: str,
    session: SessionDep,
    cache: PublicCacheDep,
    locale: LocaleQuery = "en",
) -> JournalArticleResponse:
    service = PublicContentService(session)
    return _cached(
        cache,
        key=f"{_cache_namespace(f'article:{slug}')}:{locale}",
        tags=_locale_tags(f"article:{slug}", "journal-list", locale=locale),
        factory=lambda: service.article(slug, locale) or (_raise_not_found()),
        parser=JournalArticleResponse.model_validate,
    )


@router.get("/search", response_model=SearchResponse)
def search(
    session: SessionDep,
    locale: LocaleQuery = "en",
    q: Annotated[str, Query(min_length=1, max_length=120)] = "",
) -> SearchResponse:
    """Search is deliberately uncached to avoid an unbounded cache key space."""

    return PublicContentService(session).search(locale, q)


def _raise_not_found() -> NoReturn:
    raise _not_found()
