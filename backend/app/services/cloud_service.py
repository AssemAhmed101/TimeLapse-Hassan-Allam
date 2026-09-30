from __future__ import annotations

from pathlib import Path
import time

from app.cloud.base import CloudStorageError, CloudStorageProvider
from app.cloud.local_mock import LocalMockCloudProvider
from app.cloud.s3 import S3CloudProvider
from app.core.config import settings
from app.services.storage_service import storage_service


class CloudService:
    def __init__(self) -> None:
        self.provider = self._build_provider()

    def _build_provider(self) -> CloudStorageProvider:
        provider = settings.CLOUD_PROVIDER.lower()

        if provider == "local_mock":
            mock_root = Path(settings.STORAGE_PATH) / "_mock_cloud"
            return LocalMockCloudProvider(mock_root)

        if provider in {"s3", "cloudflare_r2", "s3_compatible"}:
            return S3CloudProvider(
                bucket=settings.CLOUD_BUCKET,
                region=settings.AWS_REGION,
                endpoint_url=settings.AWS_ENDPOINT_URL,
                access_key=settings.AWS_ACCESS_KEY_ID,
                secret_key=settings.AWS_SECRET_ACCESS_KEY,
            )

        raise CloudStorageError(
            f"Unsupported cloud provider: {settings.CLOUD_PROVIDER}"
        )

    def status(self) -> dict:
        provider = settings.CLOUD_PROVIDER.lower()

        configured = True
        if provider in {"s3", "cloudflare_r2", "s3_compatible"}:
            configured = bool(
                settings.CLOUD_BUCKET
                and settings.AWS_ACCESS_KEY_ID
                and settings.AWS_SECRET_ACCESS_KEY
            )

        return {
            "provider": settings.CLOUD_PROVIDER,
            "configured": configured,
            "bucket": settings.CLOUD_BUCKET,
            "prefix": settings.CLOUD_PREFIX,
        }

    def object_key_for(self, local_path: Path) -> str:
        local_path = local_path.resolve()
        storage_root = Path(settings.STORAGE_PATH).resolve()

        try:
            relative = local_path.relative_to(storage_root)
        except ValueError:
            relative = Path(local_path.name)

        prefix = settings.CLOUD_PREFIX.strip("/")
        return f"{prefix}/{relative.as_posix()}" if prefix else relative.as_posix()

    def upload_file(self, local_path: Path) -> dict:
        if not local_path.exists() or not local_path.is_file():
            raise CloudStorageError(
                f"Local file does not exist: {local_path}"
            )

        object_key = self.object_key_for(local_path)

        last_error: Exception | None = None

        for attempt in range(settings.CLOUD_RETRY_COUNT + 1):
            try:
                cloud_url = self.provider.upload_file(
                    local_path,
                    object_key,
                )

                return {
                    "success": True,
                    "local_path": str(local_path),
                    "object_key": object_key,
                    "cloud_url": cloud_url,
                }

            except Exception as exc:
                last_error = exc

                if attempt < settings.CLOUD_RETRY_COUNT:
                    time.sleep(settings.CLOUD_RETRY_DELAY_SECONDS)

        raise CloudStorageError(
            str(last_error) if last_error else "Unknown cloud upload error"
        )

    def sync_storage(self) -> dict:
        storage_service.ensure_structure()

        files: list[Path] = []

        for base in (
            storage_service.snapshots_path,
            storage_service.timelapses_path,
        ):
            if not base.exists():
                continue

            for item in base.rglob("*"):
                if item.is_file() and item.name != ".gitkeep":
                    files.append(item)

        uploaded = 0
        skipped = 0
        failed = 0
        errors: list[str] = []

        for item in files:
            object_key = self.object_key_for(item)

            try:
                if self.provider.exists(object_key):
                    skipped += 1
                    continue

                self.upload_file(item)
                uploaded += 1

            except Exception as exc:
                failed += 1
                errors.append(f"{item}: {exc}")

        return {
            "scanned_files": len(files),
            "uploaded_files": uploaded,
            "skipped_files": skipped,
            "failed_files": failed,
            "errors": errors,
        }


cloud_service = CloudService()
