from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.api.public import PublicCacheDep
from app.db.session import get_session
from app.models.admin import AdminUser
from app.schemas.admin import (
    AdminRecognitionListResponse,
    AdminRecognitionResponse,
    AdminRecognitionWriteRequest,
    AdminStudioMemberListResponse,
    AdminStudioMemberResponse,
    AdminStudioMemberWriteRequest,
    StudioContentReorderRequest,
)
from app.services.studio_administration import (
    StudioAdministrationService,
    StudioContentConflictError,
    StudioContentNotFoundError,
    StudioContentPublishingValidationError,
    StudioContentReorderError,
)

router = APIRouter(tags=["admin studio"])
SessionDep = Annotated[Session, Depends(get_session)]
StudioContentKind = Literal["people", "recognition"]


def _service(session: Session, cache: PublicCacheDep) -> StudioAdministrationService:
    return StudioAdministrationService(session, cache)


def _not_found(kind: StudioContentKind) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{kind} entry not found")


def _conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="studio content order conflicts"
    )


def _cache_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="public cache invalidation is temporarily unavailable",
    )


def _publishing_invalid(error: StudioContentPublishingValidationError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"message": str(error), "fields": error.fields},
    )


@router.get("/people", response_model=AdminStudioMemberListResponse)
def list_people(
    _administrator: AdministratorDep, session: SessionDep, cache: PublicCacheDep
) -> AdminStudioMemberListResponse:
    return _service(session, cache).list_people()


@router.post(
    "/people", response_model=AdminStudioMemberResponse, status_code=status.HTTP_201_CREATED
)
def create_person(
    payload: AdminStudioMemberWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminStudioMemberResponse:
    try:
        return _service(session, cache).create_person(payload, authenticated[0])
    except StudioContentPublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/people/order", response_model=AdminStudioMemberListResponse)
def reorder_people(
    payload: StudioContentReorderRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminStudioMemberListResponse:
    try:
        response = _service(session, cache).reorder("people", payload, authenticated[0])
        assert isinstance(response, AdminStudioMemberListResponse)
        return response
    except StudioContentReorderError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/people/{record_id}", response_model=AdminStudioMemberResponse)
def update_person(
    record_id: UUID,
    payload: AdminStudioMemberWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminStudioMemberResponse:
    try:
        return _service(session, cache).update_person(record_id, payload, authenticated[0])
    except StudioContentNotFoundError as error:
        session.rollback()
        raise _not_found("people") from error
    except StudioContentPublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.delete("/people/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    record_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> None:
    _delete("people", record_id, authenticated[0], session, cache)


@router.get("/recognition", response_model=AdminRecognitionListResponse)
def list_recognitions(
    _administrator: AdministratorDep, session: SessionDep, cache: PublicCacheDep
) -> AdminRecognitionListResponse:
    return _service(session, cache).list_recognitions()


@router.post(
    "/recognition", response_model=AdminRecognitionResponse, status_code=status.HTTP_201_CREATED
)
def create_recognition(
    payload: AdminRecognitionWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminRecognitionResponse:
    try:
        return _service(session, cache).create_recognition(payload, authenticated[0])
    except StudioContentPublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/recognition/order", response_model=AdminRecognitionListResponse)
def reorder_recognitions(
    payload: StudioContentReorderRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminRecognitionListResponse:
    try:
        response = _service(session, cache).reorder("recognition", payload, authenticated[0])
        assert isinstance(response, AdminRecognitionListResponse)
        return response
    except StudioContentReorderError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/recognition/{record_id}", response_model=AdminRecognitionResponse)
def update_recognition(
    record_id: UUID,
    payload: AdminRecognitionWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminRecognitionResponse:
    try:
        return _service(session, cache).update_recognition(record_id, payload, authenticated[0])
    except StudioContentNotFoundError as error:
        session.rollback()
        raise _not_found("recognition") from error
    except StudioContentPublishingValidationError as error:
        session.rollback()
        raise _publishing_invalid(error) from error
    except StudioContentConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.delete("/recognition/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recognition(
    record_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> None:
    _delete("recognition", record_id, authenticated[0], session, cache)


def _delete(
    kind: StudioContentKind,
    record_id: UUID,
    administrator: AdminUser,
    session: Session,
    cache: PublicCacheDep,
) -> None:
    try:
        _service(session, cache).delete(kind, record_id, administrator)
    except StudioContentNotFoundError as error:
        session.rollback()
        raise _not_found(kind) from error
    except RedisError as error:
        raise _cache_unavailable() from error
