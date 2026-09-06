from __future__ import annotations

import time
from os import getenv

import pytest
from PIL import Image
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.content import MediaAsset, MediaProcessingState
from app.services.media_storage import MediaStorage
from app.tasks.media import process_media_asset_task

pytestmark = pytest.mark.skipif(
    getenv("VOLUMA_RUN_MEDIA_WORKER_INTEGRATION") != "1",
    reason="requires an explicitly provisioned PostgreSQL, Redis, and Celery worker",
)


def test_real_worker_creates_ready_derivatives_through_redis() -> None:
    settings = get_settings()
    storage = MediaStorage(settings.media_root)
    storage.ensure_layout()
    with SessionLocal() as session:
        asset = MediaAsset(
            original_extension="png",
            source_content_type="image/png",
            source_size_bytes=1,
            source_width=180,
            source_height=120,
            processing_state=MediaProcessingState.PROCESSING,
            alt_en="Worker integration image",
            alt_fa="تصویر آزمون پردازشگر",
        )
        session.add(asset)
        session.commit()
        media_id = asset.id
    source = storage.source_path(media_id, "png")
    source.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (180, 120), color=(42, 56, 72)).save(source, "PNG")

    process_media_asset_task.delay(str(media_id))
    deadline = time.monotonic() + 45
    state = MediaProcessingState.PROCESSING
    derivative_version: str | None = None
    while time.monotonic() < deadline:
        with SessionLocal() as session:
            processed = session.scalar(select(MediaAsset).where(MediaAsset.id == media_id))
            assert processed is not None
            state = processed.processing_state
            derivative_version = processed.derivative_version
        if state in {MediaProcessingState.READY, MediaProcessingState.FAILED}:
            break
        time.sleep(0.25)

    try:
        assert state == MediaProcessingState.READY
        assert derivative_version is not None
        derivative_directory = storage.public_directory(media_id, derivative_version)
        assert (derivative_directory / "w640.avif").is_file()
        assert (derivative_directory / "w1024.webp").is_file()
        assert (derivative_directory / "og.webp").is_file()
    finally:
        storage.remove_media(media_id)


def test_real_worker_recovers_after_a_transient_missing_source() -> None:
    settings = get_settings()
    storage = MediaStorage(settings.media_root)
    storage.ensure_layout()
    with SessionLocal() as session:
        asset = MediaAsset(
            original_extension="png",
            source_content_type="image/png",
            source_size_bytes=1,
            source_width=180,
            source_height=120,
            processing_state=MediaProcessingState.PROCESSING,
        )
        session.add(asset)
        session.commit()
        media_id = asset.id

    process_media_asset_task.delay(str(media_id))
    first_failure_deadline = time.monotonic() + 15
    attempts = 0
    state = MediaProcessingState.PROCESSING
    while time.monotonic() < first_failure_deadline:
        with SessionLocal() as session:
            processed = session.scalar(select(MediaAsset).where(MediaAsset.id == media_id))
            assert processed is not None
            state = processed.processing_state
            attempts = processed.processing_attempts
        if state == MediaProcessingState.FAILED and attempts >= 1:
            break
        time.sleep(0.05)

    try:
        assert state == MediaProcessingState.FAILED
        source = storage.source_path(media_id, "png")
        source.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (180, 120), color=(42, 56, 72)).save(source, "PNG")

        recovery_deadline = time.monotonic() + 20
        while time.monotonic() < recovery_deadline:
            with SessionLocal() as session:
                processed = session.scalar(select(MediaAsset).where(MediaAsset.id == media_id))
                assert processed is not None
                state = processed.processing_state
                attempts = processed.processing_attempts
            if state in {MediaProcessingState.READY, MediaProcessingState.FAILED} and attempts >= 2:
                if state == MediaProcessingState.READY:
                    break
            time.sleep(0.1)

        assert state == MediaProcessingState.READY
        assert attempts >= 2
    finally:
        storage.remove_media(media_id)
