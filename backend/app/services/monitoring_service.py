from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import platform
import time

from sqlalchemy import text

from app.core.config import settings
from app.database.session import SessionLocal
from app.repositories.camera_repository import camera_repository
from app.repositories.snapshot_repository import snapshot_repository
from app.services.cloud_service import cloud_service
from app.services.scheduler_service import scheduler_service
from app.services.storage_service import storage_service


class MonitoringService:
    def __init__(self) -> None:
        self.started_at = datetime.now(timezone.utc)
        self.started_monotonic = time.monotonic()

    @staticmethod
    def evaluate_status(
        *,
        database_ok: bool,
        scheduler_running: bool,
        storage_warning: bool,
        cloud_configured: bool,
    ) -> tuple[str, list[str]]:
        warnings: list[str] = []

        if not database_ok:
            warnings.append("database_unavailable")

        if not scheduler_running:
            warnings.append("scheduler_not_running")

        if storage_warning:
            warnings.append("storage_low_space")

        if not cloud_configured:
            warnings.append("cloud_not_configured")

        if not database_ok:
            return "critical", warnings

        if warnings:
            return "degraded", warnings

        return "ok", warnings

    def database_status(self) -> dict:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return {"ok": True, "error": None}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        finally:
            db.close()

    def camera_status(self) -> dict:
        db = SessionLocal()
        try:
            cameras = camera_repository.list(db)
            enabled = [camera for camera in cameras if camera.is_enabled]

            latest_snapshot_at = None
            for camera in cameras:
                snapshot = snapshot_repository.get_last_for_camera(db, camera.id)
                if snapshot is None:
                    continue

                captured_at = snapshot.captured_at
                if latest_snapshot_at is None or captured_at > latest_snapshot_at:
                    latest_snapshot_at = captured_at

            return {
                "total": len(cameras),
                "enabled": len(enabled),
                "disabled": len(cameras) - len(enabled),
                "latest_snapshot_at": (
                    latest_snapshot_at.isoformat()
                    if latest_snapshot_at
                    else None
                ),
            }
        finally:
            db.close()

    def health(self) -> dict:
        database = self.database_status()
        scheduler = scheduler_service.status()
        storage = storage_service.status()
        cloud = cloud_service.status()
        cameras = self.camera_status()

        overall, warnings = self.evaluate_status(
            database_ok=database["ok"],
            scheduler_running=bool(scheduler["running"]),
            storage_warning=bool(storage["disk"]["warning"]),
            cloud_configured=bool(cloud["configured"]),
        )

        return {
            "status": overall,
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(
                time.monotonic() - self.started_monotonic,
                2,
            ),
            "started_at": self.started_at.isoformat(),
            "application": {
                "name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "python": platform.python_version(),
            },
            "database": database,
            "scheduler": scheduler,
            "storage": storage,
            "cloud": cloud,
            "cameras": cameras,
        }

    def read_logs(self, limit: int = 100) -> dict:
        limit = max(1, min(limit, 500))
        log_file = Path(settings.LOG_PATH) / "timelapse.log"

        if not log_file.exists():
            return {
                "file": str(log_file),
                "lines": [],
                "count": 0,
            }

        try:
            lines = log_file.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        except OSError as exc:
            return {
                "file": str(log_file),
                "lines": [],
                "count": 0,
                "error": str(exc),
            }

        selected = lines[-limit:]

        return {
            "file": str(log_file),
            "lines": selected,
            "count": len(selected),
        }


monitoring_service = MonitoringService()
