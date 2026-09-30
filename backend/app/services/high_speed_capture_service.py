from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import math
import threading
import time

from fastapi import HTTPException

from app.database.session import SessionLocal
from app.repositories.snapshot_repository import snapshot_repository
from app.services.camera_service import camera_service


@dataclass
class CaptureJob:
    camera_id: int
    interval_seconds: float
    duration_seconds: int
    expected_snapshots: int
    started_at: datetime
    expected_end_at: datetime
    running: bool = True
    state: str = "running"
    captured_snapshots: int = 0
    failed_snapshots: int = 0
    first_snapshot_at: datetime | None = None
    last_snapshot_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None
    stop_event: threading.Event = field(default_factory=threading.Event, repr=False)


class HighSpeedCaptureService:
    """Short-duration, best-effort high-frequency snapshot capture.

    This is intentionally in-memory and designed for controlled test sessions.
    It does not replace the normal scheduler. The minimum supported target
    interval is 0.5 seconds; real capture speed is limited by NVR/camera/network
    response time.
    """

    def __init__(self) -> None:
        self._jobs: dict[int, CaptureJob] = {}
        self._lock = threading.Lock()

    def start(self, *, camera_id: int, interval_seconds: float, duration_seconds: int) -> dict:
        if interval_seconds < 0.5:
            raise HTTPException(status_code=422, detail="Minimum interval is 0.5 seconds")
        if duration_seconds < 10 or duration_seconds > 1800:
            raise HTTPException(status_code=422, detail="Duration must be between 10 and 1800 seconds")

        db = SessionLocal()
        try:
            camera = camera_service.get_camera(db, camera_id)
            if not camera.is_enabled:
                raise HTTPException(status_code=409, detail="Camera is disabled")
            # Build provider while ORM object is attached; provider contains only copied settings.
            provider = camera_service.build_provider(camera)
        finally:
            db.close()

        with self._lock:
            existing = self._jobs.get(camera_id)
            if existing and existing.running:
                raise HTTPException(status_code=409, detail="A high-speed capture test is already running for this camera")

            now = datetime.now(timezone.utc)
            job = CaptureJob(
                camera_id=camera_id,
                interval_seconds=float(interval_seconds),
                duration_seconds=int(duration_seconds),
                expected_snapshots=max(1, math.ceil(duration_seconds / interval_seconds)),
                started_at=now,
                expected_end_at=now + timedelta(seconds=duration_seconds),
            )
            self._jobs[camera_id] = job

        thread = threading.Thread(
            target=self._run,
            args=(job, provider),
            name=f"high-speed-capture-{camera_id}",
            daemon=True,
        )
        thread.start()
        return self.status(camera_id)

    def _run(self, job: CaptureJob, provider) -> None:
        start_mono = time.monotonic()
        next_due = start_mono

        while not job.stop_event.is_set():
            now_mono = time.monotonic()
            elapsed = now_mono - start_mono
            if elapsed >= job.duration_seconds:
                break

            if now_mono < next_due:
                job.stop_event.wait(min(next_due - now_mono, 0.1))
                continue

            captured_at = datetime.now(timezone.utc)
            db = SessionLocal()
            try:
                file_path = provider.capture_snapshot()
                snapshot_repository.create(
                    db=db,
                    camera_id=job.camera_id,
                    file_path=str(file_path),
                )
                job.captured_snapshots += 1
                if job.first_snapshot_at is None:
                    job.first_snapshot_at = captured_at
                job.last_snapshot_at = captured_at
                job.last_error = None
            except Exception as exc:
                job.failed_snapshots += 1
                job.last_error = str(exc)
            finally:
                db.close()

            # Keep a target cadence without launching overlapping requests.
            next_due += job.interval_seconds
            if next_due < time.monotonic():
                next_due = time.monotonic()

        job.running = False
        job.finished_at = datetime.now(timezone.utc)
        job.state = "stopped" if job.stop_event.is_set() else "completed"

    def stop(self, camera_id: int) -> dict:
        with self._lock:
            job = self._jobs.get(camera_id)
            if job is None:
                raise HTTPException(status_code=404, detail="No high-speed capture test found for this camera")
            job.stop_event.set()
        return self.status(camera_id)

    def status(self, camera_id: int) -> dict:
        with self._lock:
            job = self._jobs.get(camera_id)
            if job is None:
                return {
                    "camera_id": camera_id,
                    "running": False,
                    "state": "idle",
                    "expected_snapshots": 0,
                    "captured_snapshots": 0,
                    "failed_snapshots": 0,
                    "elapsed_seconds": 0.0,
                    "remaining_seconds": 0.0,
                    "progress_percent": 0.0,
                }

            now = datetime.now(timezone.utc)
            end_for_elapsed = job.finished_at or now
            elapsed = max(0.0, (end_for_elapsed - job.started_at).total_seconds())
            remaining = max(0.0, job.duration_seconds - elapsed) if job.running else 0.0
            progress = min(100.0, (elapsed / job.duration_seconds * 100.0)) if job.duration_seconds else 0.0
            if not job.running and job.state == "completed":
                progress = 100.0

            def iso(value):
                return value.isoformat() if value else None

            return {
                "camera_id": job.camera_id,
                "running": job.running,
                "state": job.state,
                "interval_seconds": job.interval_seconds,
                "duration_seconds": job.duration_seconds,
                "expected_snapshots": job.expected_snapshots,
                "captured_snapshots": job.captured_snapshots,
                "failed_snapshots": job.failed_snapshots,
                "started_at": iso(job.started_at),
                "expected_end_at": iso(job.expected_end_at),
                "finished_at": iso(job.finished_at),
                "first_snapshot_at": iso(job.first_snapshot_at),
                "last_snapshot_at": iso(job.last_snapshot_at),
                "elapsed_seconds": round(elapsed, 1),
                "remaining_seconds": round(remaining, 1),
                "progress_percent": round(progress, 1),
                "last_error": job.last_error,
            }


high_speed_capture_service = HighSpeedCaptureService()
