from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil

from app.core.config import settings


@dataclass
class CleanupCandidate:
    path: Path
    size: int


class StorageService:
    def __init__(self, root_path: Path | None = None) -> None:
        self.root_path = Path(root_path or settings.STORAGE_PATH)
        self.snapshots_path = self.root_path / "snapshots"
        self.timelapses_path = self.root_path / "timelapses"

    def ensure_structure(self) -> None:
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        self.timelapses_path.mkdir(parents=True, exist_ok=True)

    def camera_snapshot_dir(self, camera_id: int) -> Path:
        path = self.snapshots_path / f"camera_{camera_id:03d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def camera_timelapse_dir(self, camera_id: int) -> Path:
        path = self.timelapses_path / f"camera_{camera_id:03d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def category_stats(self, path: Path) -> dict:
        file_count = 0
        total_bytes = 0

        if path.exists():
            for item in path.rglob("*"):
                if item.is_file() and item.name != ".gitkeep":
                    file_count += 1
                    try:
                        total_bytes += item.stat().st_size
                    except OSError:
                        continue

        return {
            "file_count": file_count,
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 ** 2), 3),
            "total_gb": round(total_bytes / (1024 ** 3), 3),
        }

    def disk_stats(self) -> dict:
        self.ensure_structure()
        usage = shutil.disk_usage(self.root_path)
        used = usage.total - usage.free
        percent = (used / usage.total * 100) if usage.total else 0.0
        free_gb = usage.free / (1024 ** 3)

        return {
            "total_bytes": usage.total,
            "used_bytes": used,
            "free_bytes": usage.free,
            "free_gb": round(free_gb, 3),
            "usage_percent": round(percent, 2),
            "warning": self.warning_level(percent) != "normal",
            "warning_level": self.warning_level(percent),
        }

    @staticmethod
    def warning_level(usage_percent: float) -> str:
        levels = sorted(
            float(value.strip())
            for value in settings.STORAGE_WARNING_LEVELS.split(",")
            if value.strip()
        )
        if len(levels) != 3:
            levels = [70.0, 85.0, 95.0]
        if usage_percent >= levels[2]:
            return "critical"
        if usage_percent >= levels[1]:
            return "high"
        if usage_percent >= levels[0]:
            return "warning"
        return "normal"

    @staticmethod
    def forecast() -> dict:
        cameras = settings.EXPECTED_CAMERA_COUNT
        captures = settings.CAPTURES_PER_CAMERA_PER_DAY
        daily_images = cameras * captures
        annual_images = daily_images * 365
        annual_gb = annual_images * settings.ASSUMED_IMAGE_SIZE_MB / 1024
        years = (
            settings.STORAGE_CAPACITY_GB / annual_gb
            if annual_gb > 0
            else 0.0
        )
        return {
            "configured_capacity_gb": settings.STORAGE_CAPACITY_GB,
            "camera_count": cameras,
            "captures_per_camera_per_day": captures,
            "total_images_per_day": daily_images,
            "annual_images": annual_images,
            "assumed_image_size_mb": settings.ASSUMED_IMAGE_SIZE_MB,
            "estimated_annual_gb": round(annual_gb, 3),
            "estimated_capacity_years": round(years, 2),
        }

    def status(self) -> dict:
        self.ensure_structure()

        return {
            "root_path": str(self.root_path),
            "snapshots": self.category_stats(self.snapshots_path),
            "timelapses": self.category_stats(self.timelapses_path),
            "disk": self.disk_stats(),
            "forecast": self.forecast(),
        }

    def cleanup(
        self,
        *,
        dry_run: bool = True,
        snapshot_retention_days: int | None = None,
        timelapse_retention_days: int | None = None,
    ) -> dict:
        self.ensure_structure()

        snapshot_days = (
            snapshot_retention_days
            if snapshot_retention_days is not None
            else settings.SNAPSHOT_RETENTION_DAYS
        )
        timelapse_days = (
            timelapse_retention_days
            if timelapse_retention_days is not None
            else settings.TIMELAPSE_RETENTION_DAYS
        )

        now = datetime.now(timezone.utc)

        candidates: list[CleanupCandidate] = []
        scanned_files = 0
        errors: list[str] = []

        for base_path, retention_days in (
            (self.snapshots_path, snapshot_days),
            (self.timelapses_path, timelapse_days),
        ):
            if retention_days == 0:
                continue
            cutoff = now - timedelta(days=retention_days)

            if not base_path.exists():
                continue

            for item in base_path.rglob("*"):
                if not item.is_file() or item.name == ".gitkeep":
                    continue

                scanned_files += 1

                try:
                    stat = item.stat()
                    modified = datetime.fromtimestamp(
                        stat.st_mtime,
                        tz=timezone.utc,
                    )
                except OSError as exc:
                    errors.append(f"{item}: {exc}")
                    continue

                if modified < cutoff:
                    candidates.append(
                        CleanupCandidate(
                            path=item,
                            size=stat.st_size,
                        )
                    )

        deleted_files = 0
        freed_bytes = 0

        if not dry_run:
            for candidate in candidates:
                try:
                    candidate.path.unlink(missing_ok=True)
                    deleted_files += 1
                    freed_bytes += candidate.size
                except OSError as exc:
                    errors.append(f"{candidate.path}: {exc}")

            self._remove_empty_dirs(self.snapshots_path)
            self._remove_empty_dirs(self.timelapses_path)

        return {
            "dry_run": dry_run,
            "scanned_files": scanned_files,
            "matched_files": len(candidates),
            "deleted_files": deleted_files,
            "freed_bytes": freed_bytes,
            "freed_mb": round(freed_bytes / (1024 ** 2), 3),
            "errors": errors,
        }

    @staticmethod
    def _remove_empty_dirs(base_path: Path) -> None:
        if not base_path.exists():
            return

        directories = sorted(
            (p for p in base_path.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        )

        for directory in directories:
            try:
                if not any(directory.iterdir()):
                    directory.rmdir()
            except OSError:
                continue


storage_service = StorageService()
