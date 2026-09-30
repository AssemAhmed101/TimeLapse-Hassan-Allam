import logging
import threading
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories.camera_repository import camera_repository
from app.services.snapshot_engine import snapshot_engine

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    BackgroundScheduler = None
    IntervalTrigger = None
    APSCHEDULER_AVAILABLE = False


class SchedulerService:
    DISPATCH_SECONDS = 30

    def __init__(self) -> None:
        self._running = False
        self._dispatcher_registered = False
        self._next_run_time: datetime | None = None
        self._last_cycle_at: datetime | None = None
        self._last_cycle_success: bool | None = None
        self._last_cycle_error: str | None = None
        self._cycle_count = 0
        self._failed_cycle_count = 0

        self._fallback_thread: threading.Thread | None = None
        self._fallback_stop_event = threading.Event()

        self.scheduler = None
        if APSCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler(
                timezone="UTC",
                job_defaults={
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": 60,
                },
            )

    def start(self) -> None:
        if self._running:
            return

        if APSCHEDULER_AVAILABLE and self.scheduler is not None:
            self.scheduler.start()

            if self.scheduler.get_job("snapshot_dispatcher") is None:
                self.scheduler.add_job(
                    self.run_snapshot_cycle,
                    trigger=IntervalTrigger(seconds=self.DISPATCH_SECONDS),
                    id="snapshot_dispatcher",
                    replace_existing=True,
                )

            self._dispatcher_registered = True
            self._running = True
            logger.info("Scheduler started using APScheduler")
            return

        self._start_fallback_scheduler()
        logger.info("Scheduler started using threading fallback")

    def _start_fallback_scheduler(self) -> None:
        self._fallback_stop_event.clear()
        self._running = True
        self._dispatcher_registered = True
        self._next_run_time = datetime.now(timezone.utc) + timedelta(
            seconds=self.DISPATCH_SECONDS
        )

        self._fallback_thread = threading.Thread(
            target=self._fallback_loop,
            name="snapshot-dispatcher",
            daemon=True,
        )
        self._fallback_thread.start()

    def _fallback_loop(self) -> None:
        while not self._fallback_stop_event.wait(self.DISPATCH_SECONDS):
            try:
                self.run_snapshot_cycle()
            except Exception:
                logger.exception("Fallback snapshot scheduler cycle failed")
            finally:
                self._next_run_time = datetime.now(timezone.utc) + timedelta(
                    seconds=self.DISPATCH_SECONDS
                )

    def shutdown(self) -> None:
        if not self._running:
            return

        if APSCHEDULER_AVAILABLE and self.scheduler is not None:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
        else:
            self._fallback_stop_event.set()

            if (
                self._fallback_thread is not None
                and self._fallback_thread.is_alive()
            ):
                self._fallback_thread.join(timeout=1)

        self._running = False
        self._dispatcher_registered = False
        self._next_run_time = None

        logger.info("Scheduler stopped")

    def run_snapshot_cycle(self) -> dict:
        db: Session = SessionLocal()
        self._last_cycle_at = datetime.now(timezone.utc)
        self._cycle_count += 1

        try:
            cameras = camera_repository.list(db)
            results = []

            for camera in cameras:
                result = snapshot_engine.run_once(
                    db=db,
                    camera_id=camera.id,
                    force=False,
                )
                results.append(result.model_dump())

            self._last_cycle_success = True
            self._last_cycle_error = None

            return {
                "camera_count": len(cameras),
                "results": results,
            }

        except Exception as exc:
            self._last_cycle_success = False
            self._last_cycle_error = str(exc)
            self._failed_cycle_count += 1
            logger.exception("Snapshot scheduler cycle failed")
            raise

        finally:
            db.close()

    def status(self) -> dict:
        if APSCHEDULER_AVAILABLE and self.scheduler is not None:
            job = self.scheduler.get_job("snapshot_dispatcher")

            return {
                "running": bool(self.scheduler.running),
                "dispatcher_registered": job is not None,
                "dispatcher_job_id": job.id if job else None,
                "next_run_time": (
                    job.next_run_time.isoformat()
                    if job and job.next_run_time
                    else None
                ),
                "engine": "apscheduler",
                "last_cycle_at": (
                    self._last_cycle_at.isoformat()
                    if self._last_cycle_at
                    else None
                ),
                "last_cycle_success": self._last_cycle_success,
                "last_cycle_error": self._last_cycle_error,
                "cycle_count": self._cycle_count,
                "failed_cycle_count": self._failed_cycle_count,
            }

        return {
            "running": self._running,
            "dispatcher_registered": self._dispatcher_registered,
            "dispatcher_job_id": (
                "snapshot_dispatcher"
                if self._dispatcher_registered
                else None
            ),
            "next_run_time": (
                self._next_run_time.isoformat()
                if self._next_run_time
                else None
            ),
            "engine": "threading_fallback",
            "last_cycle_at": (
                self._last_cycle_at.isoformat()
                if self._last_cycle_at
                else None
            ),
            "last_cycle_success": self._last_cycle_success,
            "last_cycle_error": self._last_cycle_error,
            "cycle_count": self._cycle_count,
            "failed_cycle_count": self._failed_cycle_count,
        }


scheduler_service = SchedulerService()
