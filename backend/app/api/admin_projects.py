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
    AdminProjectFormOptionsResponse,
    AdminProjectListResponse,
    AdminProjectResponse,
    ProjectBlocksReplaceRequest,
    ProjectCreateRequest,
    ProjectReorderRequest,
    ProjectUpdateRequest,
)
from app.services.project_administration import (
    ProjectAdministrationService,
    ProjectNotFoundError,
    ProjectPublishingValidationError,
    ProjectReorderError,
    ProjectSlugConflictError,
    ProjectTaxonomyError,
)

router = APIRouter(prefix="/projects", tags=["admin projects"])
SessionDep = Annotated[Session, Depends(get_session)]


def _service(session: Session, cache: PublicCacheDep) -> ProjectAdministrationService:
    return ProjectAdministrationService(session, cache)


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")


def _conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="project slug or order conflicts"
    )


def _cache_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="public cache invalidation is temporarily unavailable",
    )


@router.get("", response_model=AdminProjectListResponse)
def list_projects(
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectListResponse:
    return _service(session, cache).list_projects()


@router.post("", response_model=AdminProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectResponse:
    try:
        return _service(session, cache).create(payload, authenticated[0])
    except ProjectSlugConflictError as error:
        session.rollback()
        raise _conflict() from error
    except ProjectTaxonomyError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except ProjectPublishingValidationError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": "project cannot be published", "fields": error.fields},
        ) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.get("/form-options", response_model=AdminProjectFormOptionsResponse)
def project_form_options(
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectFormOptionsResponse:
    return _service(session, cache).form_options()


@router.put("/order", response_model=AdminProjectListResponse)
def reorder_projects(
    payload: ProjectReorderRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectListResponse:
    try:
        return _service(session, cache).reorder(payload, authenticated[0])
    except ProjectReorderError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except ProjectSlugConflictError as error:
        session.rollback()
        raise _conflict() from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.get("/{project_id}", response_model=AdminProjectResponse)
def get_project(
    project_id: UUID,
    _administrator: AdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectResponse:
    try:
        return _service(session, cache).project(project_id)
    except ProjectNotFoundError as error:
        raise _not_found() from error


@router.put("/{project_id}", response_model=AdminProjectResponse)
def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectResponse:
    try:
        return _service(session, cache).update(project_id, payload, authenticated[0])
    except ProjectNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except ProjectSlugConflictError as error:
        session.rollback()
        raise _conflict() from error
    except ProjectTaxonomyError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except ProjectPublishingValidationError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": "project cannot be published", "fields": error.fields},
        ) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.put("/{project_id}/blocks", response_model=AdminProjectResponse)
def replace_project_blocks(
    project_id: UUID,
    payload: ProjectBlocksReplaceRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminProjectResponse:
    try:
        return _service(session, cache).replace_blocks(project_id, payload, authenticated[0])
    except ProjectNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except ProjectSlugConflictError as error:
        session.rollback()
        raise _conflict() from error
    except ProjectPublishingValidationError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": "project cannot be published", "fields": error.fields},
        ) from error
    except RedisError as error:
        raise _cache_unavailable() from error


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> None:
    try:
        _service(session, cache).delete(project_id, authenticated[0])
    except ProjectNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except RedisError as error:
        raise _cache_unavailable() from error
