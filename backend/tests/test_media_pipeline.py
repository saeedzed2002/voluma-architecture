from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import UploadFile
from PIL import Image
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.admin import AdminUser
from app.models.content import (
    JournalArticle,
    JournalArticleBlock,
    JournalCategory,
    MediaAsset,
    MediaProcessingState,
    Project,
    PublicationState,
)
from app.schemas.admin import (
    MediaAssetMetadataWriteRequest,
    ProjectMediaReplaceRequest,
    ProjectMediaWriteItem,
)
from app.services.media_administration import (
    MediaAdministrationService,
    MediaInUseError,
    MediaQueueError,
)
from app.services.media_storage import (
    MediaStorage,
    MediaUploadValidationError,
    generate_derivatives,
)
from app.services.public_content import PublicContentService
from app.tasks import media as media_tasks


class RecordingCache:
    def __init__(self) -> None:
        self.invalidated: list[set[str]] = []

    def invalidate(self, tags: set[str]) -> None:
        self.invalidated.append(tags)


def _image_bytes() -> bytes:
    destination = BytesIO()
    Image.new("RGB", (96, 64), color=(24, 36, 48)).save(destination, "PNG")
    return destination.getvalue()


def _upload(data: bytes) -> UploadFile:
    return UploadFile(filename="untrusted-name.png", file=BytesIO(data))


def _stage(storage: MediaStorage, data: bytes, *, max_bytes: int = 50 * 1024 * 1024):
    return asyncio.run(
        storage.stage_upload(
            _upload(data),
            max_bytes=max_bytes,
            max_dimension=12_000,
            max_pixels=100_000_000,
        )
    )


def _administrator(session: Session) -> AdminUser:
    administrator = AdminUser(
        email="media-admin@example.com",
        password_hash="not-used-in-service-test",
        is_active=True,
    )
    session.add(administrator)
    session.flush()
    return administrator


def test_upload_boundary_accepts_exactly_50_mib_and_rejects_one_extra_byte(tmp_path: Path) -> None:
    storage = MediaStorage(tmp_path / "media")
    image = _image_bytes()
    at_limit = image + (b"\0" * (50 * 1024 * 1024 - len(image)))
    staged = _stage(storage, at_limit)
    assert staged.source.size_bytes == 50 * 1024 * 1024
    assert staged.source.extension == "png"
    storage.remove_tree(staged.directory)

    with pytest.raises(MediaUploadValidationError, match="50 MiB"):
        _stage(storage, at_limit + b"\0")


def test_derivative_generation_creates_verified_avif_and_webp(tmp_path: Path) -> None:
    storage = MediaStorage(tmp_path / "media")
    staged = _stage(storage, _image_bytes())
    width, height = generate_derivatives(staged.source_path, staged.directory / "derived")

    assert (width, height) == (96, 64)
    assert (staged.directory / "derived" / "w640.avif").is_file()
    assert (staged.directory / "derived" / "w1024.webp").is_file()
    assert (staged.directory / "derived" / "placeholder.webp").is_file()
    with Image.open(staged.directory / "derived" / "w640.avif") as derivative:
        assert derivative.format == "AVIF"


def test_queue_failure_is_durable_and_preserves_original(session: Session, tmp_path: Path) -> None:
    storage = MediaStorage(tmp_path / "media")
    staged = _stage(storage, _image_bytes())
    administrator = _administrator(session)

    def unavailable_queue(_: object) -> None:
        raise OSError("broker unavailable")

    service = MediaAdministrationService(
        session,
        storage,
        RecordingCache(),  # type: ignore[arg-type]
        enqueue_processing=unavailable_queue,
    )
    with pytest.raises(MediaQueueError):
        service.create_from_staged(staged, administrator)

    asset = session.scalar(select(MediaAsset))
    assert asset is not None
    assert asset.processing_state == MediaProcessingState.FAILED
    assert asset.processing_error == "media processing could not be queued"
    assert storage.source_path(asset.id, asset.original_extension).is_file()


def test_ready_media_can_be_ordered_and_selected_as_project_cover(
    session: Session, tmp_path: Path
) -> None:
    project = session.scalar(select(Project).order_by(Project.display_order))
    assert project is not None
    administrator = _administrator(session)
    first = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.READY,
        derivative_version="version-one",
        derivative_width=20,
        derivative_height=10,
        alt_en="First image",
        alt_fa="تصویر نخست",
    )
    second = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.READY,
        derivative_version="version-two",
        derivative_width=20,
        derivative_height=10,
        alt_en="Second image",
        alt_fa="تصویر دوم",
    )
    session.add_all((first, second))
    session.commit()
    cache = RecordingCache()
    service = MediaAdministrationService(session, MediaStorage(tmp_path / "media"), cache)  # type: ignore[arg-type]

    response = service.replace_project_media(
        project.id,
        ProjectMediaReplaceRequest(
            items=[
                ProjectMediaWriteItem(media_id=second.id, is_cover=True),
                ProjectMediaWriteItem(media_id=first.id, is_cover=False),
            ]
        ),
        administrator,
    )

    assert [item.media.id for item in response.items] == [second.id, first.id]
    assert response.items[0].is_cover is True
    assert cache.invalidated
    public_project = PublicContentService(session).project(project.slug, "en")
    assert public_project is not None
    assert public_project.cover_image is not None
    assert public_project.cover_image.url.endswith(f"/{second.id}/version-two/w1024.webp")
    assert public_project.cover_image.avif_srcset is not None


def test_project_media_rejects_duplicate_assets_before_replacing_the_gallery() -> None:
    asset_id = uuid4()

    with pytest.raises(ValidationError, match="assets must be unique"):
        ProjectMediaReplaceRequest(
            items=[
                ProjectMediaWriteItem(media_id=asset_id, is_cover=True),
                ProjectMediaWriteItem(media_id=asset_id, is_cover=False),
            ]
        )


def test_retry_requeues_failed_asset_with_retained_source(session: Session, tmp_path: Path) -> None:
    storage = MediaStorage(tmp_path / "media")
    administrator = _administrator(session)
    asset = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.FAILED,
        processing_attempts=1,
        processing_error="image processing failed (OSError)",
    )
    session.add(asset)
    session.commit()
    source = storage.source_path(asset.id, asset.original_extension)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"retained source")
    queued: list[object] = []
    service = MediaAdministrationService(
        session,
        storage,
        RecordingCache(),  # type: ignore[arg-type]
        enqueue_processing=queued.append,
    )

    response = service.retry(asset.id, administrator)

    assert response.processing_state == MediaProcessingState.PROCESSING
    assert response.processing_error is None
    assert queued == [asset.id]


def test_journal_cover_media_invalidates_public_content_and_cannot_be_deleted(
    session: Session, tmp_path: Path
) -> None:
    administrator = _administrator(session)
    asset = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.READY,
        derivative_version="journal-cover-version",
        derivative_width=20,
        derivative_height=10,
        alt_en="Initial journal cover",
        alt_fa="تصویر روی جلد اولیه",
    )
    category = JournalCategory(
        slug="journal-cover-tests",
        title_en="Journal cover tests",
        title_fa="آزمون‌های روی جلد یادداشت",
        display_order=99,
    )
    article = JournalArticle(
        slug="journal-managed-cover",
        publication_state=PublicationState.PUBLISHED,
        category=category,
        title_en="Managed journal cover",
        title_fa="روی جلد مدیریت‌شدهٔ یادداشت",
        excerpt_en="An article with a managed cover image.",
        excerpt_fa="یادداشتی با تصویر روی جلد مدیریت‌شده.",
        body_en="A complete body.",
        body_fa="بدنه‌ای کامل.",
        reading_minutes=1,
        cover_media=asset,
    )
    session.add(article)
    session.commit()
    cache = RecordingCache()
    service = MediaAdministrationService(
        session,
        MediaStorage(tmp_path / "media"),
        cache,  # type: ignore[arg-type]
        enqueue_cleanup=lambda _: None,
    )

    service.update_metadata(
        asset.id,
        MediaAssetMetadataWriteRequest(
            alt_en="Updated journal cover",
            alt_fa="تصویر روی جلد به‌روزشده",
            caption_en=None,
            caption_fa=None,
            credit=None,
        ),
        administrator,
    )

    assert cache.invalidated[-1] >= {
        "home",
        "journal-list",
        "journal-list:en",
        "journal-list:fa",
        "article:journal-managed-cover",
        "article:journal-managed-cover:en",
        "article:journal-managed-cover:fa",
    }
    with pytest.raises(MediaInUseError, match="journal article"):
        service.delete(asset.id, administrator)


def test_journal_block_media_invalidates_public_content_and_cannot_be_deleted(
    session: Session, tmp_path: Path
) -> None:
    administrator = _administrator(session)
    asset = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.READY,
        derivative_version="journal-block-version",
        derivative_width=20,
        derivative_height=10,
        alt_en="Initial journal image",
        alt_fa="تصویر اولیهٔ یادداشت",
    )
    session.add(asset)
    session.flush()
    category = JournalCategory(
        slug="journal-block-tests",
        title_en="Journal block tests",
        title_fa="آزمون‌های بلوک یادداشت",
        display_order=100,
    )
    article = JournalArticle(
        slug="journal-managed-block",
        publication_state=PublicationState.PUBLISHED,
        category=category,
        title_en="Managed journal block",
        title_fa="بلوک مدیریت‌شدهٔ یادداشت",
        excerpt_en="An article with an in-body managed image.",
        excerpt_fa="یادداشتی با تصویر مدیریت‌شده در متن.",
        body_en="A complete body.",
        body_fa="بدنه‌ای کامل.",
        reading_minutes=1,
        blocks=[
            JournalArticleBlock(
                block_type="single_image",
                content_en={"media_id": str(asset.id)},
                content_fa={"media_id": str(asset.id)},
                display_order=0,
            )
        ],
    )
    session.add(article)
    session.commit()
    cache = RecordingCache()
    service = MediaAdministrationService(
        session,
        MediaStorage(tmp_path / "media"),
        cache,  # type: ignore[arg-type]
        enqueue_cleanup=lambda _: None,
    )

    service.update_metadata(
        asset.id,
        MediaAssetMetadataWriteRequest(
            alt_en="Updated journal image",
            alt_fa="تصویر به‌روزشدهٔ یادداشت",
            caption_en=None,
            caption_fa=None,
            credit=None,
        ),
        administrator,
    )

    assert cache.invalidated[-1] >= {
        "journal-list",
        "journal-list:en",
        "journal-list:fa",
        "article:journal-managed-block",
        "article:journal-managed-block:en",
        "article:journal-managed-block:fa",
    }
    with pytest.raises(MediaInUseError, match="journal article block"):
        service.delete(asset.id, administrator)


def test_transient_processing_failure_is_durable_and_propagates_for_celery_retry(
    monkeypatch: pytest.MonkeyPatch, session: Session, tmp_path: Path
) -> None:
    storage = MediaStorage(tmp_path / "media")
    asset = MediaAsset(
        original_extension="png",
        source_content_type="image/png",
        source_size_bytes=100,
        source_width=20,
        source_height=10,
        processing_state=MediaProcessingState.PROCESSING,
    )
    session.add(asset)
    session.commit()
    source = storage.source_path(asset.id, asset.original_extension)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(_image_bytes())

    def unavailable_derivative_generation(*_: object) -> tuple[int, int]:
        raise OSError("temporary media volume failure")

    monkeypatch.setattr(media_tasks, "_storage", lambda: storage)
    monkeypatch.setattr(media_tasks, "generate_derivatives", unavailable_derivative_generation)
    monkeypatch.setattr(
        media_tasks,
        "SessionLocal",
        sessionmaker(bind=session.get_bind(), expire_on_commit=False),
    )

    with pytest.raises(OSError, match="temporary media volume failure"):
        media_tasks.process_media_asset(asset.id)

    session.expire_all()
    persisted = session.scalar(select(MediaAsset).where(MediaAsset.id == asset.id))
    assert persisted is not None
    assert persisted.processing_state == MediaProcessingState.FAILED
    assert persisted.processing_attempts == 1
    assert storage.source_path(asset.id, asset.original_extension).is_file()
