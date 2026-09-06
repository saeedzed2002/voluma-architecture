from __future__ import annotations

import os
import shutil
import warnings
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps

ALLOWED_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}
DERIVATIVE_WIDTHS = (320, 640, 1024, 1600, 2400)


class MediaUploadValidationError(ValueError):
    """An uploaded file violates VOLUMA's image-source contract."""


@dataclass(frozen=True)
class SourceImage:
    extension: str
    content_type: str
    height: int
    size_bytes: int
    width: int


@dataclass(frozen=True)
class StagedUpload:
    directory: Path
    source: SourceImage
    source_path: Path


class MediaStorage:
    """Filesystem contract shared by the API and Celery worker.

    The only caller-controlled identifier is a UUID created by the application.  This
    deliberately keeps originals and staging files outside the Nginx-exposed tree.
    """

    def __init__(self, root: Path) -> None:
        self.root = root

    def ensure_layout(self) -> None:
        for directory in (self.originals_root, self.public_root, self.staging_root):
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def originals_root(self) -> Path:
        return self.root / "originals"

    @property
    def public_root(self) -> Path:
        return self.root / "public"

    @property
    def staging_root(self) -> Path:
        return self.root / "staging"

    async def stage_upload(
        self,
        upload: UploadFile,
        *,
        max_bytes: int,
        max_dimension: int,
        max_pixels: int,
    ) -> StagedUpload:
        self.ensure_layout()
        directory = self.staging_root / f"upload-{uuid4().hex}"
        directory.mkdir(mode=0o700)
        source_path = directory / "source"
        size_bytes = 0
        try:
            with source_path.open("xb") as destination:
                while chunk := await upload.read(1024 * 1024):
                    size_bytes += len(chunk)
                    if size_bytes > max_bytes:
                        raise MediaUploadValidationError("image exceeds the 50 MiB upload limit")
                    destination.write(chunk)
            if size_bytes == 0:
                raise MediaUploadValidationError("image upload is empty")
            source = self.inspect_source(
                source_path,
                size_bytes=size_bytes,
                max_dimension=max_dimension,
                max_pixels=max_pixels,
            )
            return StagedUpload(directory=directory, source=source, source_path=source_path)
        except BaseException:
            self.remove_tree(directory)
            raise
        finally:
            await upload.close()

    def inspect_source(
        self,
        source_path: Path,
        *,
        size_bytes: int,
        max_dimension: int,
        max_pixels: int,
    ) -> SourceImage:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(source_path) as image:
                    image.load()
                    image_format = image.format
                    width, height = image.size
                    animated = (
                        bool(getattr(image, "is_animated", False))
                        or int(getattr(image, "n_frames", 1)) != 1
                    )
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise MediaUploadValidationError("image exceeds the safe pixel limit") from error
        except (OSError, ValueError, SyntaxError) as error:
            raise MediaUploadValidationError("uploaded file is not a decodable image") from error
        if image_format not in ALLOWED_FORMATS:
            raise MediaUploadValidationError("only JPEG, PNG, and WebP images are accepted")
        if animated:
            raise MediaUploadValidationError("animated images are not accepted")
        if width > max_dimension or height > max_dimension:
            raise MediaUploadValidationError("image dimensions exceed the 12000 pixel limit")
        if width * height > max_pixels:
            raise MediaUploadValidationError("image exceeds the 100000000 pixel limit")
        extension, content_type = ALLOWED_FORMATS[image_format]
        return SourceImage(
            extension=extension,
            content_type=content_type,
            height=height,
            size_bytes=size_bytes,
            width=width,
        )

    def persist_source(self, staged: StagedUpload, media_id: UUID) -> Path:
        destination_directory = self.original_directory(media_id)
        destination_directory.mkdir(parents=True, exist_ok=False)
        destination = destination_directory / f"source.{staged.source.extension}"
        os.replace(staged.source_path, destination)
        self.remove_tree(staged.directory)
        return destination

    def original_directory(self, media_id: UUID) -> Path:
        return self.originals_root / str(media_id)

    def source_path(self, media_id: UUID, extension: str) -> Path:
        return self.original_directory(media_id) / f"source.{extension}"

    def public_directory(self, media_id: UUID, derivative_version: str) -> Path:
        return self.public_root / str(media_id) / derivative_version

    def public_url(self, media_id: UUID, derivative_version: str, filename: str) -> str:
        return f"/media/{media_id}/{derivative_version}/{filename}"

    def processing_directory(self, media_id: UUID, derivative_version: str) -> Path:
        return self.staging_root / f"process-{media_id}-{derivative_version}"

    def publish_directory(
        self, staged_directory: Path, media_id: UUID, derivative_version: str
    ) -> Path:
        destination = self.public_directory(media_id, derivative_version)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError("immutable media derivative version already exists")
        os.replace(staged_directory, destination)
        return destination

    def remove_media(self, media_id: UUID) -> None:
        self.remove_tree(self.original_directory(media_id))
        self.remove_tree(self.public_root / str(media_id))

    @staticmethod
    def remove_tree(path: Path) -> None:
        if path.exists():
            shutil.rmtree(path)


def generate_derivatives(source_path: Path, destination: Path) -> tuple[int, int]:
    """Create all public derivatives in an unexposed staging directory.

    Importing the plugin here registers Pillow's AVIF encoder in both API test and
    Linux worker processes.  A container integration test validates actual encoding.
    """

    import pillow_avif  # type: ignore[import-untyped]  # noqa: F401

    destination.mkdir(mode=0o700)
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(source_path) as source:
            source.load()
            image = ImageOps.exif_transpose(source).convert("RGB")
    width, height = image.size
    for target_width in DERIVATIVE_WIDTHS:
        derivative = image.copy()
        derivative.thumbnail((target_width, height), Image.Resampling.LANCZOS)
        derivative.save(destination / f"w{target_width}.webp", "WEBP", quality=82, method=6)
        derivative.save(destination / f"w{target_width}.avif", "AVIF", quality=55)
    placeholder = image.copy()
    placeholder.thumbnail((48, 48), Image.Resampling.LANCZOS)
    placeholder.save(destination / "placeholder.webp", "WEBP", quality=60, method=6)
    og = ImageOps.fit(image, (1200, 630), method=Image.Resampling.LANCZOS)
    og.save(destination / "og.webp", "WEBP", quality=82, method=6)
    expected = {
        "placeholder.webp",
        "og.webp",
        *(
            f"w{target_width}.{fmt}"
            for target_width in DERIVATIVE_WIDTHS
            for fmt in ("avif", "webp")
        ),
    }
    missing = [filename for filename in expected if not (destination / filename).is_file()]
    if missing:
        raise RuntimeError("image derivative verification failed")
    return width, height
