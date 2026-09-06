from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.api.public import PublicCacheDep
from app.db.session import get_session
from app.schemas.admin import (
    AdminBilingualContentListResponse,
    AdminBilingualContentResponse,
    AdminBilingualContentWriteRequest,
    BilingualContentReorderRequest,
)
from app.services.editorial_content_administration import (
    EditorialContentAdministrationService,
    EditorialContentConflictError,
    EditorialContentNotFoundError,
    EditorialContentPublishingValidationError,
    EditorialContentReorderError,
)

router = APIRouter(tags=["admin editorial content"])
SessionDep = Annotated[Session, Depends(get_session)]
EditorialContentKind = Literal["expertise", "process"]


def _service(session: Session, cache: PublicCacheDep) -> EditorialContentAdministrationService:
    return EditorialContentAdministrationService(session, cache)


def _not_found(kind: EditorialContentKind) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{kind} entry not found")


def _conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="editorial content order conflicts"
    )


def _cache_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="public cache invalidation is temporarily unavailable",
    )


def _publishing_invalid(error: EditorialContentPublishingValidationError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"message": str(error), "fields": error.fields},
    )


def _routes(kind: EditorialContentKind) -> None:
    @router.get(f"/{kind}", response_model=AdminBilingualContentListResponse)
    def list_entries(
        _administrator: AdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminBilingualContentListResponse:
        return _service(session, cache).list_entries(kind)

    @router.post(
        f"/{kind}",
        response_model=AdminBilingualContentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_entry(
        payload: AdminBilingualContentWriteRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminBilingualContentResponse:
        try:
            return _service(session, cache).create(kind, payload, authenticated[0])
        except EditorialContentPublishingValidationError as error:
            session.rollback()
            raise _publishing_invalid(error) from error
        except EditorialContentConflictError as error:
            session.rollback()
            raise _conflict() from error
        except RedisError as error:
            raise _cache_unavailable() from error

    @router.put(f"/{kind}/order", response_model=AdminBilingualContentListResponse)
    def reorder_entries(
        payload: BilingualContentReorderRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminBilingualContentListResponse:
        try:
            return _service(session, cache).reorder(kind, payload, authenticated[0])
        except EditorialContentReorderError as error:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        except EditorialContentConflictError as error:
            session.rollback()
            raise _conflict() from error
        except RedisError as error:
            raise _cache_unavailable() from error

    @router.put(f"/{kind}/{{record_id}}", response_model=AdminBilingualContentResponse)
    def update_entry(
        record_id: UUID,
        payload: AdminBilingualContentWriteRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminBilingualContentResponse:
        try:
            return _service(session, cache).update(kind, record_id, payload, authenticated[0])
        except EditorialContentNotFoundError as error:
            session.rollback()
            raise _not_found(kind) from error
        except EditorialContentPublishingValidationError as error:
            session.rollback()
            raise _publishing_invalid(error) from error
        except EditorialContentConflictError as error:
            session.rollback()
            raise _conflict() from error
        except RedisError as error:
            raise _cache_unavailable() from error

    @router.delete(f"/{kind}/{{record_id}}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_entry(
        record_id: UUID,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> None:
        try:
            _service(session, cache).delete(kind, record_id, authenticated[0])
        except EditorialContentNotFoundError as error:
            session.rollback()
            raise _not_found(kind) from error
        except RedisError as error:
            raise _cache_unavailable() from error


_routes("expertise")
_routes("process")
