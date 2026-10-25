"""File storage service: magic bytes validation, safe naming and persistence.

Security rules enforced here:

* the **real** content type is determined from the binary magic bytes, never
  from the client supplied ``Content-Type`` header or file extension;
* only ``image/jpeg``, ``image/png``, ``image/webp`` and ``application/pdf``
  are accepted (PDF only for purchase receipts);
* every file is capped at 5 MB;
* the original filename is discarded and replaced by a random UUIDv4;
* photos are re-encoded to WebP, which also strips any embedded payload.
"""

from __future__ import annotations

import io
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import puremagic
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.errors import PayloadTooLargeError, ValidationError

#: Canonical extension for every accepted MIME type.
CANONICAL_EXTENSIONS: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

#: MIME types accepted for inspection photos.
ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})

#: MIME types accepted for purchase receipts (PDF included).
ALLOWED_RECEIPT_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "application/pdf"}
)


@dataclass(frozen=True)
class StoredFile:
    """Metadata about a persisted upload."""

    url: str
    filename: str
    stored_path: str
    size_bytes: int
    content_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "content_type": self.content_type,
        }


def detect_mime_type(data: bytes) -> str | None:
    """Return the real MIME type of ``data`` based on its magic bytes."""
    if not data:
        return None
    try:
        detected = puremagic.from_string(data[:4096], mime=True)
    except puremagic.PureError:
        return None
    if not detected:
        return None
    # ``puremagic`` returns the MIME type string directly when ``mime=True``.
    if isinstance(detected, (list, tuple)):
        detected = detected[0] if detected else ""
    return str(detected).lower() or None


class FileStorage:
    """Persists uploads on the local filesystem.

    The same relative layout is used in development (``backend/uploads/``) and
    in production (the ``uploads`` Docker volume mounted at ``/app/uploads``).
    """

    def __init__(
        self,
        base_dir: str | Path | None = None,
        *,
        max_size_mb: int | None = None,
        max_width: int | None = None,
        max_height: int | None = None,
        quality: int | None = None,
        max_photos: int | None = None,
    ) -> None:
        self.base_dir = Path(base_dir or settings.uploads_dir).resolve()
        self.max_size_bytes = (max_size_mb or settings.max_upload_size_mb) * 1024 * 1024
        self.max_width = max_width or settings.image_max_width
        self.max_height = max_height or settings.image_max_height
        self.quality = quality or settings.image_quality
        self.max_photos = max_photos or settings.max_inspection_photos

    # -- helpers ---------------------------------------------------------
    def _target_dir(self, subdir: str) -> Path:
        safe_subdir = "".join(
            char for char in subdir if char.isalnum() or char in {"-", "_"}
        ).strip("_") or "misc"
        now = datetime.now(timezone.utc)
        target = self.base_dir / safe_subdir / now.strftime("%Y%m")
        target.mkdir(parents=True, exist_ok=True)
        return target

    async def _read_bytes(self, upload: UploadFile) -> bytes:
        """Read the upload, enforcing the hard size limit while reading."""
        limit = self.max_size_bytes
        chunks: list[bytes] = []
        total = 0

        while True:
            chunk = await upload.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                # Stop early so an oversized payload is never fully buffered.
                raise PayloadTooLargeError(
                    f"The file exceeds the maximum size of {limit // (1024 * 1024)} MB.",
                    details={"max_size_bytes": limit},
                )
            chunks.append(chunk)

        if total == 0:
            raise ValidationError("The uploaded file is empty.")

        return b"".join(chunks)

    def _validate_mime_type(
        self, data: bytes, allowed_types: Iterable[str]
    ) -> str:
        """Validate the real MIME type detected from the magic bytes."""
        detected = detect_mime_type(data)
        allowed = {t.lower() for t in allowed_types}

        if detected is None:
            raise ValidationError(
                "Unsupported file type: the content could not be identified.",
                details={"allowed": sorted(allowed)},
            )

        if detected not in allowed:
            raise ValidationError(
                f"Unsupported file type '{detected}'. Allowed: {', '.join(sorted(allowed))}.",
                details={"detected": detected, "allowed": sorted(allowed)},
            )

        return detected

    def _build_name(self, mime_type: str) -> str:
        """Build the random, extension-only name used on disk."""
        extension = CANONICAL_EXTENSIONS.get(mime_type, ".bin")
        return f"{uuid.uuid4()}{extension}"

    def _persist(
        self, data: bytes, *, subdir: str, mime_type: str
    ) -> StoredFile:
        target_dir = self._target_dir(subdir)
        stored_name = self._build_name(mime_type)
        stored_path = target_dir / stored_name
        stored_path.write_bytes(data)

        relative = stored_path.relative_to(self.base_dir).as_posix()
        return StoredFile(
            url=f"/uploads/{relative}",
            filename=stored_name,
            stored_path=str(stored_path),
            size_bytes=len(data),
            content_type=mime_type,
        )

    # -- public API ------------------------------------------------------
    async def save_image(
        self, upload: UploadFile, *, subdir: str = "inspections"
    ) -> StoredFile:
        """Validate, resize and re-encode an image, then persist it as WebP."""
        data = await self._read_bytes(upload)
        self._validate_mime_type(data, ALLOWED_IMAGE_TYPES)

        try:
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                try:
                    from PIL import ImageOps

                    image = ImageOps.exif_transpose(image)
                except Exception:  # pragma: no cover - malformed EXIF
                    pass

                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")

                image.thumbnail((self.max_width, self.max_height), Image.LANCZOS)

                buffer = io.BytesIO()
                image.save(buffer, format="WEBP", quality=self.quality, method=4)
                processed = buffer.getvalue()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError(
                "The uploaded file could not be read as an image."
            ) from exc

        # Re-encoding to WebP also removes any payload appended to the file.
        return self._persist(processed, subdir=subdir, mime_type="image/webp")

    async def save_document(
        self, upload: UploadFile, *, subdir: str = "receipts"
    ) -> StoredFile:
        """Persist a non-image upload (a PDF purchase receipt)."""
        data = await self._read_bytes(upload)
        mime_type = self._validate_mime_type(data, ALLOWED_RECEIPT_TYPES)

        if mime_type not in {"application/pdf"}:
            # Images are handled by ``save_image`` which re-encodes them.
            return await self.save_image(upload, subdir=subdir)

        return self._persist(data, subdir=subdir, mime_type=mime_type)

    async def save_receipt(self, upload: UploadFile) -> StoredFile:
        """Persist a purchase receipt: images are compressed, PDFs kept as-is."""
        data = await self._read_bytes(upload)
        mime_type = self._validate_mime_type(data, ALLOWED_RECEIPT_TYPES)

        if mime_type == "application/pdf":
            return self._persist(data, subdir="receipts", mime_type=mime_type)

        try:
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                try:
                    from PIL import ImageOps

                    image = ImageOps.exif_transpose(image)
                except Exception:  # pragma: no cover - malformed EXIF
                    pass

                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")

                image.thumbnail((self.max_width, self.max_height), Image.LANCZOS)

                buffer = io.BytesIO()
                image.save(buffer, format="WEBP", quality=self.quality, method=4)
                processed = buffer.getvalue()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError(
                "The uploaded file could not be read as an image."
            ) from exc

        return self._persist(processed, subdir="receipts", mime_type="image/webp")

    async def save_inspection_photos(
        self, uploads: list[UploadFile]
    ) -> list[StoredFile]:
        """Persist the inspection photos of a suite item (max 5)."""
        if not uploads:
            raise ValidationError("At least one inspection photo is required.")
        if len(uploads) > self.max_photos:
            raise ValidationError(
                f"A maximum of {self.max_photos} inspection photos is allowed "
                f"per item (received {len(uploads)})."
            )

        stored: list[StoredFile] = []
        for upload in uploads:
            stored.append(await self.save_image(upload, subdir="inspections"))
        return stored

    def delete(self, stored_path: str | Path) -> bool:
        """Remove a previously stored file (path traversal safe)."""
        try:
            path = Path(stored_path).resolve()
            path.relative_to(self.base_dir)
        except (ValueError, OSError):
            return False
        if path.is_file():
            path.unlink()
            return True
        return False


#: Shared instance used across the API layer.
storage = FileStorage()
