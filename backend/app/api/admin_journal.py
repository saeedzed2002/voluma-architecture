from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.api.public import PublicCacheDep
from app.db.session import get_session
from app.schemas.admin import (
    AdminJournalArticleListResponse,
    AdminJournalArticleResponse,
    AdminJournalCategoryListResponse,
    AdminJournalCategoryResponse,
    AdminJournalCategoryWriteRequest,
    JournalArticleCreateRequest,
    JournalArticleUpdateRequest,
    JournalCategoryReorderRequest,
)
from app.services.journal_administration import (
    JournalAdministrationService,
    JournalArticleNotFoundError,
    JournalArticlePublishingValidationError,
    JournalArticleSlugConflictError,
    JournalCategoryConflictError,
    JournalCategoryInUseError,
    JournalCategoryNotFoundError,
    JournalCategoryReorderError,
)

router = APIRouter(prefix="/journal", tags=["admin journal"])
SessionDep = Annotated[Session, Depends(get_session)]


def _service(session: Session, cache: PublicCacheDep) -> JournalAdministrationService:
    return JournalAdministrationService(session, cache)


def _cache_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="public cache invalidation is temporarily unavailable",
    )


def _publishing_invalid(error: JournalArticlePublishingValidationError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"message": str(error), "fields": error.fields},
    )


@router.get("/categories", response_model=AdminJournalCategoryListResponse)
def list_categories(
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalCategoryListResponse:
    return _service(session, cache).list_categories()


@router.post(
    "/categories",
    response_model=AdminJournalCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: AdminJournalCategoryWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalCategoryResponse:
    try:
        return _service(session, cache).create_category(payload, authenticated[0])
    except JournalCategoryConflictError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="journal category slug or order conflicts",
        ) from error


@router.put("/categories/order", response_model=AdminJournalCategoryListResponse)
def reorder_categories(
    payload: JournalCategoryReorderRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalCategoryListResponse:
    try:
        return _service(session, cache).reorder_categories(payload, authenticated[0])
    except JournalCategoryReorderError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except JournalCategoryConflictError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="journal category slug or order conflicts",
        ) from error


@router.put("/categories/{category_id}", response_model=AdminJournalCategoryResponse)
def update_category(
    category_id: UUID,
    payload: AdminJournalCategoryWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalCategoryResponse:
    try:
        return _service(session, cache).update_category(category_id, payload, authenticated[0])
    except JournalCategoryNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="journal category not found"
        ) from error
    except JournalCategoryConflictError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="journal category slug or order conflicts",
        ) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> None:
    try:
        _service(session, cache).delete_category(category_id, authenticated[0])
    except JournalCategoryNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="journal category not found"
        ) from error
    except JournalCategoryInUseError as error:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("/articles", response_model=AdminJournalArticleListResponse)
def list_articles(
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalArticleListResponse:
    return _service(session, cache).list_articles()


@router.get("/articles/{article_id}", response_model=AdminJournalArticleResponse)
def get_article(
    article_id: UUID,
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalArticleResponse:
    try:
        return _service(session, cache).article(article_id)
    except JournalArticleNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="journal article not found"
        ) from error


@router.post(
    "/articles",
    response_model=AdminJournalArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    payload: JournalArticleCreateRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalArticleResponse:
    try:
        return _service(session, cache).create_article(payload, authenticated[0])
    except JournalCategoryNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="category is invalid"
        ) from error
    except JournalArticleSlugConflictError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="journal article slug conflicts"
        ) from error
    except JournalArticlePublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/articles/{article_id}", response_model=AdminJournalArticleResponse)
def update_article(
    article_id: UUID,
    payload: JournalArticleUpdateRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminJournalArticleResponse:
    try:
        return _service(session, cache).update_article(article_id, payload, authenticated[0])
    except JournalArticleNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="journal article not found"
        ) from error
    except JournalCategoryNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="category is invalid"
        ) from error
    except JournalArticleSlugConflictError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="journal article slug conflicts"
        ) from error
    except JournalArticlePublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> None:
    try:
        _service(session, cache).delete_article(article_id, authenticated[0])
    except JournalArticleNotFoundError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="journal article not found"
        ) from error
    except RedisError as error:
        raise _cache_unavailable() from error
