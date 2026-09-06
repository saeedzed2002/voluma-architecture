from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.admin import AdministratorDep, CsrfAdministratorDep
from app.api.public import PublicCacheDep
from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.schemas.admin import (
    MediaAssetListResponse,
    MediaAssetMetadataWriteRequest,
    MediaAssetResponse,
)
from app.services.media_administration import (
    MediaAdministrationService,
    MediaAssetNotFoundError,
    MediaInUseError,
    MediaQueueError,
    ProjectMediaValidationError,
)
from app.services.media_storage import MediaStorage, MediaUploadValidationError

router = APIRouter(prefix="/media", tags=["admin media"])
SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def _service(
    session: Session,
    settings: Settings,
    cache: PublicCacheDep,
) -> MediaAdministrationService:
    return MediaAdministrationService(session, MediaStorage(settings.media_root), cache)


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="media asset not found")


def _invalid(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


def _unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="media processing or cache invalidation is temporarily unavailable",
    )


@router.get("", response_model=MediaAssetListResponse)
def list_media(
    _administrator: AdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> MediaAssetListResponse:
    return _service(session, settings, cache).list_assets()


@router.post("", response_model=MediaAssetResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_media(
    file: Annotated[UploadFile, File(description="JPEG, PNG, or WebP source image")],
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> MediaAssetResponse:
    storage = MediaStorage(settings.media_root)
    try:
        staged = await storage.stage_upload(
            file,
            max_bytes=settings.media_max_upload_bytes,
            max_dimension=settings.media_max_dimension,
            max_pixels=settings.media_max_pixels,
        )
    except MediaUploadValidationError as error:
        detail = str(error)
        code = (
            status.HTTP_413_CONTENT_TOO_LARGE
            if "50 MiB" in detail
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        raise HTTPException(status_code=code, detail=detail) from error
    try:
        return _service(session, settings, cache).create_from_staged(staged, authenticated[0])
    except MediaQueueError as error:
        raise _unavailable() from error


@router.get("/{media_id}", response_model=MediaAssetResponse)
def get_media(
    media_id: UUID,
    _administrator: AdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> MediaAssetResponse:
    try:
        return _service(session, settings, cache).asset(media_id)
    except MediaAssetNotFoundError as error:
        raise _not_found() from error


@router.put("/{media_id}", response_model=MediaAssetResponse)
def update_media_metadata(
    media_id: UUID,
    payload: MediaAssetMetadataWriteRequest,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> MediaAssetResponse:
    try:
        return _service(session, settings, cache).update_metadata(
            media_id, payload, authenticated[0]
        )
    except MediaAssetNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except RedisError as error:
        raise _unavailable() from error


@router.post(
    "/{media_id}/retry", response_model=MediaAssetResponse, status_code=status.HTTP_202_ACCEPTED
)
def retry_media(
    media_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> MediaAssetResponse:
    try:
        return _service(session, settings, cache).retry(media_id, authenticated[0])
    except MediaAssetNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except ProjectMediaValidationError as error:
        session.rollback()
        raise _invalid(str(error)) from error
    except MediaQueueError as error:
        raise _unavailable() from error


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: UUID,
    authenticated: CsrfAdministratorDep,
    session: SessionDep,
    settings: SettingsDep,
    cache: PublicCacheDep,
) -> None:
    try:
        _service(session, settings, cache).delete(media_id, authenticated[0])
    except MediaAssetNotFoundError as error:
        session.rollback()
        raise _not_found() from error
    except MediaInUseError as error:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except MediaQueueError as error:
        raise _unavailable() from error
