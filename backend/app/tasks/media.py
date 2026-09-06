from __future__ import annotations

import logging
from uuid import UUID, uuid4

from PIL import UnidentifiedImageError
from sqlalchemy import select

from app.api.public import get_public_cache
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.content import MediaAsset, MediaProcessingState, ProjectMedia, PublicationState
from app.services.media_storage import MediaStorage, generate_derivatives
from app.worker import celery_app

logger = logging.getLogger(__name__)


def _storage() -> MediaStorage:
    return MediaStorage(get_settings().media_root)


def _invalidate_media_usage(media_id: UUID) -> None:
    with SessionLocal() as session:
        links = session.scalars(
            select(ProjectMedia).where(ProjectMedia.media_asset_id == media_id)
        ).all()
        tags = {
            "site",
            "home",
            "studio",
            "site:en",
            "site:fa",
            "home:en",
            "home:fa",
            "studio:en",
            "studio:fa",
        }
        for link in links:
            project = link.project
            if project.publication_state == PublicationState.PUBLISHED:
                tags.update(
                    {
                        "project-list",
                        "project-list:en",
                        "project-list:fa",
                        f"project:{project.slug}",
                        f"project:{project.slug}:en",
                        f"project:{project.slug}:fa",
                    }
                )
        try:
            get_public_cache().invalidate(tags)
        except Exception:
            logger.exception(
                "media_public_cache_invalidation_failed", extra={"media_id": str(media_id)}
            )


def _mark_failed(media_id: UUID, error: Exception) -> None:
    with SessionLocal() as session:
        asset = session.scalar(
            select(MediaAsset).where(MediaAsset.id == media_id).with_for_update()
        )
        if asset is None or asset.processing_state == MediaProcessingState.DELETED:
            return
        asset.processing_state = MediaProcessingState.FAILED
        asset.processing_error = f"image processing failed ({type(error).__name__})"
        session.commit()


def process_media_asset(media_id: UUID) -> None:
    """Produce immutable public derivatives from one durable source image."""

    storage = _storage()
    with SessionLocal() as session:
        asset = session.scalar(
            select(MediaAsset).where(MediaAsset.id == media_id).with_for_update()
        )
        if asset is None or asset.processing_state == MediaProcessingState.DELETED:
            return
        if asset.processing_state == MediaProcessingState.READY:
            return
        asset.processing_state = MediaProcessingState.PROCESSING
        asset.processing_attempts += 1
        asset.processing_error = None
        extension = asset.original_extension
        session.commit()

    derivative_version = uuid4().hex
    staging_directory = storage.processing_directory(media_id, derivative_version)
    try:
        width, height = generate_derivatives(
            storage.source_path(media_id, extension), staging_directory
        )
        storage.publish_directory(staging_directory, media_id, derivative_version)
        with SessionLocal() as session:
            asset = session.scalar(
                select(MediaAsset).where(MediaAsset.id == media_id).with_for_update()
            )
            if asset is None or asset.processing_state == MediaProcessingState.DELETED:
                return
            asset.processing_state = MediaProcessingState.READY
            asset.derivative_version = derivative_version
            asset.derivative_width = width
            asset.derivative_height = height
            asset.processing_error = None
            session.commit()
        _invalidate_media_usage(media_id)
    except UnidentifiedImageError as error:
        storage.remove_tree(staging_directory)
        _mark_failed(media_id, error)
        logger.exception("media_processing_failed", extra={"media_id": str(media_id)})
    except OSError as error:
        storage.remove_tree(staging_directory)
        _mark_failed(media_id, error)
        logger.exception("media_processing_failed", extra={"media_id": str(media_id)})
        # A durable failure state keeps the asset private while Celery retries
        # transient storage failures with its configured bounded backoff.
        raise
    except Exception as error:
        storage.remove_tree(staging_directory)
        _mark_failed(media_id, error)
        logger.exception("media_processing_failed", extra={"media_id": str(media_id)})


def cleanup_media_asset(media_id: UUID) -> None:
    storage = _storage()
    with SessionLocal() as session:
        asset = session.scalar(
            select(MediaAsset).where(MediaAsset.id == media_id).with_for_update()
        )
        if asset is None or asset.processing_state != MediaProcessingState.DELETED:
            return
        in_use = session.scalar(
            select(ProjectMedia.id).where(ProjectMedia.media_asset_id == media_id).limit(1)
        )
        if in_use is not None:
            logger.error("deleted_media_asset_still_referenced", extra={"media_id": str(media_id)})
            return
    storage.remove_media(media_id)


@celery_app.task(
    name="voluma.media.process",
    bind=True,
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)  # type: ignore[untyped-decorator]
def process_media_asset_task(self: object, media_id: str) -> None:
    process_media_asset(UUID(media_id))


@celery_app.task(
    name="voluma.media.cleanup",
    bind=True,
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)  # type: ignore[untyped-decorator]
def cleanup_media_asset_task(self: object, media_id: str) -> None:
    cleanup_media_asset(UUID(media_id))
