import time as time_module
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.snapshot_repository import snapshot_repository
from app.schemas.snapshot_policy import SnapshotEngineRunResponse
from app.services.camera_service import camera_service
from app.services.snapshot_policy_service import snapshot_policy_service


class SnapshotEngine:
    def run_once(
        self,
        db: Session,
        camera_id: int,
        force: bool = False,
    ) -> SnapshotEngineRunResponse:
        camera = camera_service.get_camera(db, camera_id)
        policy = snapshot_policy_service.get_or_create(db, camera_id)

        if not camera.is_enabled:
            return SnapshotEngineRunResponse(
                camera_id=camera_id,
                status="skipped",
                reason="camera_disabled",
            )

        if not policy.enabled:
            return SnapshotEngineRunResponse(
                camera_id=camera_id,
                status="skipped",
                reason="snapshot_policy_disabled",
            )

        now_local = datetime.now()

        if not force and not self._is_inside_capture_window(
            now_local.time(),
            policy.start_time,
            policy.end_time,
        ):
            return SnapshotEngineRunResponse(
                camera_id=camera_id,
                status="skipped",
                reason="outside_capture_window",
            )

        last_snapshot = snapshot_repository.get_last_for_camera(db, camera_id)

        if (
            not force
            and last_snapshot is not None
            and last_snapshot.captured_at is not None
        ):
            now_utc = datetime.now(timezone.utc)
            captured_at = last_snapshot.captured_at

            if captured_at.tzinfo is None:
                captured_at = captured_at.replace(tzinfo=timezone.utc)

            elapsed = (now_utc - captured_at).total_seconds()

            if elapsed < policy.interval_seconds:
                return SnapshotEngineRunResponse(
                    camera_id=camera_id,
                    status="skipped",
                    reason="interval_not_elapsed",
                )

        provider = camera_service.build_provider(camera)

        attempts = policy.retry_count + 1
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                file_path = provider.capture_snapshot()

                snapshot = snapshot_repository.create(
                    db=db,
                    camera_id=camera.id,
                    file_path=str(file_path),
                )

                return SnapshotEngineRunResponse(
                    camera_id=camera_id,
                    status="captured",
                    snapshot_id=snapshot.id,
                    file_path=str(file_path),
                )

            except Exception as exc:
                last_error = exc

                if attempt < attempts - 1 and policy.retry_delay_seconds > 0:
                    time_module.sleep(policy.retry_delay_seconds)

        return SnapshotEngineRunResponse(
            camera_id=camera_id,
            status="failed",
            reason=str(last_error) if last_error else "unknown_error",
        )

    @staticmethod
    def _is_inside_capture_window(current, start, end) -> bool:
        # Normal same-day window (the project default covers 00:00-23:59:59).
        if start < end:
            return start <= current <= end

        # Overnight window, for optional non-default policies.
        return current >= start or current <= end


snapshot_engine = SnapshotEngine()
