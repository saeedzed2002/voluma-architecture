from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.admin import AdminUser
from app.models.content import (
    MediaAsset,
    MediaProcessingState,
    Project,
    ProjectMedia,
    PublicationState,
)
from app.schemas.admin import (
    MediaAssetListResponse,
    MediaAssetMetadataWriteRequest,
    MediaAssetResponse,
    ProjectMediaListResponse,
    ProjectMediaReplaceRequest,
    ProjectMediaResponse,
)
from app.services.admin_auth import record_audit_event
from app.services.media_storage import MediaStorage, StagedUpload
from app.services.public_cache import TaggedPublicCache


class MediaAdministrationError(RuntimeError):
    """Base error for explicit media-library workflow outcomes."""


class MediaAssetNotFoundError(MediaAdministrationError):
    pass


class MediaQueueError(MediaAdministrationError):
    pass


class MediaInUseError(MediaAdministrationError):
    pass


class ProjectMediaValidationError(MediaAdministrationError):
    pass


def enqueue_media_processing(media_id: UUID) -> None:
    from app.tasks.media import process_media_asset_task

    process_media_asset_task.delay(str(media_id))


def enqueue_media_cleanup(media_id: UUID) -> None:
    from app.tasks.media import cleanup_media_asset_task

    cleanup_media_asset_task.delay(str(media_id))


class MediaAdministrationService:
    """Transactional media-library, project-gallery, and queueing workflows."""

    def __init__(
        self,
        session: Session,
        storage: MediaStorage,
        cache: TaggedPublicCache,
        *,
        enqueue_processing: Callable[[UUID], None] = enqueue_media_processing,
        enqueue_cleanup: Callable[[UUID], None] = enqueue_media_cleanup,
    ) -> None:
        self.session = session
        self.storage = storage
        self.cache = cache
        self.enqueue_processing = enqueue_processing
        self.enqueue_cleanup = enqueue_cleanup

    def list_assets(self) -> MediaAssetListResponse:
        assets = self.session.scalars(
            select(MediaAsset)
            .where(MediaAsset.processing_state != MediaProcessingState.DELETED)
            .order_by(MediaAsset.created_at.desc(), MediaAsset.id.desc())
        ).all()
        return MediaAssetListResponse(
            items=[media_asset_response(asset, self.storage) for asset in assets]
        )

    def asset(self, media_id: UUID) -> MediaAssetResponse:
        return media_asset_response(self._asset_or_raise(media_id), self.storage)

    def create_from_staged(
        self, staged: StagedUpload, administrator: AdminUser
    ) -> MediaAssetResponse:
        asset = MediaAsset(
            original_extension=staged.source.extension,
            source_content_type=staged.source.content_type,
            source_size_bytes=staged.source.size_bytes,
            source_width=staged.source.width,
            source_height=staged.source.height,
            processing_state=MediaProcessingState.PROCESSING,
        )
        self.session.add(asset)
        self.session.flush()
        try:
            self.storage.persist_source(staged, asset.id)
            record_audit_event(
                self.session,
                actor_id=administrator.id,
                action="media.uploaded",
                target_type="media_asset",
                target_id=asset.id,
            )
            self.session.commit()
        except BaseException:
            self.session.rollback()
            self.storage.remove_media(asset.id)
            raise
        try:
            self.enqueue_processing(asset.id)
        except Exception as error:
            asset = self._asset_or_raise(asset.id, lock=True)
            asset.processing_state = MediaProcessingState.FAILED
            asset.processing_error = "media processing could not be queued"
            record_audit_event(
                self.session,
                actor_id=administrator.id,
                action="media.queue_failed",
                target_type="media_asset",
                target_id=asset.id,
            )
            self.session.commit()
            raise MediaQueueError("media processing could not be queued") from error
        return media_asset_response(asset, self.storage)

    def update_metadata(
        self,
        media_id: UUID,
        payload: MediaAssetMetadataWriteRequest,
        administrator: AdminUser,
    ) -> MediaAssetResponse:
        asset = self._asset_or_raise(media_id, lock=True)
        for field in ("alt_en", "alt_fa", "caption_en", "caption_fa", "credit"):
            setattr(asset, field, getattr(payload, field))
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="media.metadata_updated",
            target_type="media_asset",
            target_id=asset.id,
        )
        self.session.commit()
        self._invalidate_media_usage(asset.id)
        return media_asset_response(asset, self.storage)

    def retry(self, media_id: UUID, administrator: AdminUser) -> MediaAssetResponse:
        asset = self._asset_or_raise(media_id, lock=True)
        if asset.processing_state != MediaProcessingState.FAILED:
            raise ProjectMediaValidationError("only failed media assets can be retried")
        if not self.storage.source_path(asset.id, asset.original_extension).is_file():
            raise ProjectMediaValidationError("the retained source image is unavailable")
        asset.processing_state = MediaProcessingState.PROCESSING
        asset.processing_error = None
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="media.retry_requested",
            target_type="media_asset",
            target_id=asset.id,
        )
        self.session.commit()
        try:
            self.enqueue_processing(asset.id)
        except Exception as error:
            asset = self._asset_or_raise(asset.id, lock=True)
            asset.processing_state = MediaProcessingState.FAILED
            asset.processing_error = "media processing could not be queued"
            self.session.commit()
            raise MediaQueueError("media processing could not be queued") from error
        return media_asset_response(asset, self.storage)

    def delete(self, media_id: UUID, administrator: AdminUser) -> None:
        asset = self._asset_or_raise(media_id, lock=True)
        if (
            self.session.scalar(
                select(ProjectMedia.id).where(ProjectMedia.media_asset_id == asset.id).limit(1)
            )
            is not None
        ):
            raise MediaInUseError("remove the asset from every project before deletion")
        asset.processing_state = MediaProcessingState.DELETED
        asset.deleted_at = datetime.now(UTC)
        asset.processing_error = None
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="media.soft_deleted",
            target_type="media_asset",
            target_id=asset.id,
        )
        self.session.commit()
        try:
            self.enqueue_cleanup(asset.id)
        except Exception as error:
            raise MediaQueueError("media cleanup could not be queued") from error

    def project_media(self, project_id: UUID) -> ProjectMediaListResponse:
        project = self._project_or_raise(project_id)
        return ProjectMediaListResponse(
            items=[project_media_response(link, self.storage) for link in project.media_links]
        )

    def replace_project_media(
        self,
        project_id: UUID,
        payload: ProjectMediaReplaceRequest,
        administrator: AdminUser,
    ) -> ProjectMediaListResponse:
        project = self._project_or_raise(project_id, lock=True)
        requested_ids = [item.media_id for item in payload.items]
        assets = (
            self.session.scalars(
                select(MediaAsset).where(MediaAsset.id.in_(requested_ids)).with_for_update()
            ).all()
            if requested_ids
            else []
        )
        assets_by_id = {asset.id: asset for asset in assets}
        if set(assets_by_id) != set(requested_ids):
            raise ProjectMediaValidationError("one or more media assets were not found")
        for asset in assets:
            if asset.processing_state != MediaProcessingState.READY or asset.deleted_at is not None:
                raise ProjectMediaValidationError(
                    "only ready media assets can be placed in a project"
                )
            if not asset.alt_en or not asset.alt_fa:
                raise ProjectMediaValidationError("project media requires localized alt text")
        for link in project.media_links:
            self.session.delete(link)
        self.session.flush()
        for display_order, item in enumerate(payload.items):
            project.media_links.append(
                ProjectMedia(
                    media=assets_by_id[item.media_id],
                    display_order=display_order,
                    is_cover=item.is_cover,
                )
            )
        record_audit_event(
            self.session,
            actor_id=administrator.id,
            action="project.media_replaced",
            target_type="project",
            target_id=project.id,
        )
        self.session.commit()
        if project.publication_state == PublicationState.PUBLISHED:
            self._invalidate_project(project.slug)
        return self.project_media(project.id)

    def _asset_or_raise(self, media_id: UUID, *, lock: bool = False) -> MediaAsset:
        statement = select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.processing_state != MediaProcessingState.DELETED,
        )
        if lock:
            statement = statement.with_for_update()
        asset = self.session.scalar(statement)
        if asset is None:
            raise MediaAssetNotFoundError()
        return asset

    def _project_or_raise(self, project_id: UUID, *, lock: bool = False) -> Project:
        statement = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.media_links).selectinload(ProjectMedia.media))
        )
        if lock:
            statement = statement.with_for_update()
        project = self.session.scalar(statement)
        if project is None:
            raise ProjectMediaValidationError("project was not found")
        return project

    def _invalidate_project(self, slug: str) -> None:
        self.cache.invalidate(
            {
                "home",
                "project-list",
                f"project:{slug}",
                "home:en",
                "home:fa",
                "project-list:en",
                "project-list:fa",
                f"project:{slug}:en",
                f"project:{slug}:fa",
            }
        )

    def _invalidate_media_usage(self, media_id: UUID) -> None:
        links = self.session.scalars(
            select(ProjectMedia)
            .where(ProjectMedia.media_asset_id == media_id)
            .options(selectinload(ProjectMedia.project))
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
            if link.project.publication_state == PublicationState.PUBLISHED:
                tags.update(
                    {
                        "project-list",
                        "project-list:en",
                        "project-list:fa",
                        f"project:{link.project.slug}",
                        f"project:{link.project.slug}:en",
                        f"project:{link.project.slug}:fa",
                    }
                )
        try:
            self.cache.invalidate(tags)
        except RedisError:
            raise


def media_asset_response(asset: MediaAsset, storage: MediaStorage) -> MediaAssetResponse:
    preview_url = None
    placeholder_url = None
    if (
        asset.processing_state == MediaProcessingState.READY
        and asset.derivative_version is not None
    ):
        preview_url = storage.public_url(asset.id, asset.derivative_version, "w640.webp")
        placeholder_url = storage.public_url(asset.id, asset.derivative_version, "placeholder.webp")
    return MediaAssetResponse(
        id=asset.id,
        original_extension=asset.original_extension,
        source_content_type=asset.source_content_type,
        source_size_bytes=asset.source_size_bytes,
        source_width=asset.source_width,
        source_height=asset.source_height,
        processing_state=asset.processing_state,
        processing_attempts=asset.processing_attempts,
        processing_error=asset.processing_error,
        derivative_version=asset.derivative_version,
        derivative_width=asset.derivative_width,
        derivative_height=asset.derivative_height,
        preview_url=preview_url,
        placeholder_url=placeholder_url,
        alt_en=asset.alt_en,
        alt_fa=asset.alt_fa,
        caption_en=asset.caption_en,
        caption_fa=asset.caption_fa,
        credit=asset.credit,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


def project_media_response(link: ProjectMedia, storage: MediaStorage) -> ProjectMediaResponse:
    return ProjectMediaResponse(
        media=media_asset_response(link.media, storage),
        display_order=link.display_order,
        is_cover=link.is_cover,
    )
