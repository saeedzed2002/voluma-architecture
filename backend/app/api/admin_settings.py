from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.api.public import PublicCacheDep
from app.db.session import get_session
from app.schemas.admin import AdminSiteSettingsResponse, SiteSettingsWriteRequest
from app.services.site_settings_administration import (
    SiteSettingsAdministrationService,
    SiteSettingsConflictError,
)

router = APIRouter(tags=["admin settings"])
SessionDep = Annotated[Session, Depends(get_session)]


def _service(session: Session, cache: PublicCacheDep) -> SiteSettingsAdministrationService:
    return SiteSettingsAdministrationService(session, cache)


@router.get("/settings", response_model=AdminSiteSettingsResponse)
def get_settings(
    _administrator: AdministratorDep, session: SessionDep, cache: PublicCacheDep
) -> AdminSiteSettingsResponse:
    return _service(session, cache).get()


@router.put("/settings", response_model=AdminSiteSettingsResponse)
def update_settings(
    payload: SiteSettingsWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    cache: PublicCacheDep,
) -> AdminSiteSettingsResponse:
    try:
        return _service(session, cache).update(payload, authenticated[0])
    except SiteSettingsConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="site settings changed concurrently; refresh and retry",
        ) from error
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="public cache invalidation is temporarily unavailable",
        ) from error
