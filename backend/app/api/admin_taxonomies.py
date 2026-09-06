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
    AdminTaxonomyListResponse,
    AdminTaxonomyResponse,
    AdminTaxonomyWriteRequest,
    TaxonomyReorderRequest,
)
from app.services.taxonomy_administration import (
    TaxonomyAdministrationService,
    TaxonomyConflictError,
    TaxonomyInUseError,
    TaxonomyNotFoundError,
    TaxonomyReorderError,
)

router = APIRouter(tags=["admin taxonomies"])
SessionDep = Annotated[Session, Depends(get_session)]
TaxonomyKind = Literal["discipline", "typology"]


def _service(session: Session, cache: PublicCacheDep) -> TaxonomyAdministrationService:
    return TaxonomyAdministrationService(session, cache)


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="taxonomy not found")


def _conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="taxonomy slug or order conflicts"
    )


def _cache_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="public cache invalidation is temporarily unavailable",
    )


def _routes(kind: TaxonomyKind, plural: str) -> None:
    @router.get(f"/{plural}", response_model=AdminTaxonomyListResponse)
    def list_taxonomy(
        _administrator: AdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminTaxonomyListResponse:
        return _service(session, cache).list_taxonomies(kind)

    @router.post(
        f"/{plural}", response_model=AdminTaxonomyResponse, status_code=status.HTTP_201_CREATED
    )
    def create_taxonomy(
        payload: AdminTaxonomyWriteRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminTaxonomyResponse:
        try:
            return _service(session, cache).create(kind, payload, authenticated[0])
        except TaxonomyConflictError as error:
            session.rollback()
            raise _conflict() from error

    @router.put(f"/{plural}/order", response_model=AdminTaxonomyListResponse)
    def reorder_taxonomy(
        payload: TaxonomyReorderRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminTaxonomyListResponse:
        try:
            return _service(session, cache).reorder(kind, payload, authenticated[0])
        except TaxonomyReorderError as error:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        except TaxonomyConflictError as error:
            session.rollback()
            raise _conflict() from error
        except RedisError as error:
            raise _cache_unavailable() from error

    @router.put(f"/{plural}/{{record_id}}", response_model=AdminTaxonomyResponse)
    def update_taxonomy(
        record_id: UUID,
        payload: AdminTaxonomyWriteRequest,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> AdminTaxonomyResponse:
        try:
            return _service(session, cache).update(kind, record_id, payload, authenticated[0])
        except TaxonomyNotFoundError as error:
            session.rollback()
            raise _not_found() from error
        except TaxonomyConflictError as error:
            session.rollback()
            raise _conflict() from error
        except RedisError as error:
            raise _cache_unavailable() from error

    @router.delete(f"/{plural}/{{record_id}}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_taxonomy(
        record_id: UUID,
        authenticated: CsrfAdministratorDep,
        session: SessionDep,
        cache: PublicCacheDep,
    ) -> None:
        try:
            _service(session, cache).delete(kind, record_id, authenticated[0])
        except TaxonomyNotFoundError as error:
            session.rollback()
            raise _not_found() from error
        except TaxonomyInUseError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        except RedisError as error:
            raise _cache_unavailable() from error


_routes("discipline", "disciplines")
_routes("typology", "typologies")
