from datetime import datetime
from math import ceil
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.snapshot_repository import snapshot_repository
from app.repositories.timelapse_repository import timelapse_repository
from app.schemas.timelapse import TimeLapseCreateRequest
from app.services.camera_service import camera_service
from app.services.cloud_service import cloud_service
from app.services.storage_service import storage_service
from app.utils.ffmpeg import FFmpegError, build_timelapse


class TimeLapseService:
    def list(self, db: Session, camera_id: int | None = None):
        return timelapse_repository.list(db, camera_id)

    def get(self, db: Session, timelapse_id: int):
        item = timelapse_repository.get(db, timelapse_id)

        if item is None:
            raise HTTPException(status_code=404, detail="Time-lapse not found")

        return item

    def get_video_file(self, db: Session, timelapse_id: int) -> Path:
        item = self.get(db, timelapse_id)

        if item.status != "completed":
            raise HTTPException(
                status_code=409,
                detail="Time-lapse is not completed yet",
            )

        path = Path(item.file_path).resolve()

        if not path.exists() or not path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Time-lapse video file is missing from storage",
            )

        return path

    def library(
        self,
        db: Session,
        *,
        camera_id: int | None,
        status: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
        page: int,
        page_size: int,
    ) -> dict:
        if start_at and end_at and end_at < start_at:
            raise HTTPException(
                status_code=422,
                detail="end_at must be after start_at",
            )

        allowed_statuses = {"processing", "completed", "failed"}
        if status and status not in allowed_statuses:
            raise HTTPException(
                status_code=422,
                detail="Invalid time-lapse status",
            )

        items, total = timelapse_repository.library_page(
            db,
            camera_id=camera_id,
            status=status,
            start_at=start_at,
            end_at=end_at,
            page=page,
            page_size=page_size,
        )

        pages = ceil(total / page_size) if total else 0

        response_items = []

        for item in items:
            path = Path(item.file_path)
            can_stream = (
                item.status == "completed"
                and path.exists()
                and path.is_file()
            )

            response_items.append({
                "id": item.id,
                "camera_id": item.camera_id,
                "status": item.status,
                "period_start": item.period_start,
                "period_end": item.period_end,
                "created_at": item.created_at,
                "filename": path.name,
                "video_url": (
                    f"/api/v1/timelapses/{item.id}/video"
                    if can_stream
                    else None
                ),
                "download_url": (
                    f"/api/v1/timelapses/{item.id}/download"
                    if can_stream
                    else None
                ),
            })

        return {
            "items": response_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    def preview(
        self,
        db: Session,
        camera_id: int,
        start_at: datetime,
        end_at: datetime,
        fps: int,
    ) -> dict:
        camera_service.get_camera(db, camera_id)

        if end_at <= start_at:
            raise HTTPException(
                status_code=422,
                detail="end_at must be after start_at",
            )

        snapshots = snapshot_repository.list_between(
            db=db,
            camera_id=camera_id,
            start_at=start_at,
            end_at=end_at,
        )

        count = len(snapshots)

        return {
            "camera_id": camera_id,
            "snapshot_count": count,
            "can_generate": count >= 2,
            "fps": fps,
            "estimated_duration_seconds": round(count / fps, 2) if fps else 0.0,
            "first_snapshot_at": snapshots[0].captured_at if snapshots else None,
            "last_snapshot_at": snapshots[-1].captured_at if snapshots else None,
        }

    def generate(
        self,
        db: Session,
        data: TimeLapseCreateRequest,
    ):
        camera_service.get_camera(db, data.camera_id)

        if data.end_at <= data.start_at:
            raise HTTPException(
                status_code=422,
                detail="end_at must be after start_at",
            )

        snapshots = snapshot_repository.list_between(
            db=db,
            camera_id=data.camera_id,
            start_at=data.start_at,
            end_at=data.end_at,
        )

        if len(snapshots) < 2:
            raise HTTPException(
                status_code=422,
                detail="At least 2 snapshots are required to generate a time-lapse",
            )

        camera_dir = storage_service.camera_timelapse_dir(data.camera_id)

        filename = (
            f"timelapse_{data.start_at:%Y%m%d_%H%M%S}"
            f"_to_{data.end_at:%Y%m%d_%H%M%S}.mp4"
        )
        output_path = camera_dir / filename

        record = timelapse_repository.create(
            db,
            camera_id=data.camera_id,
            file_path=str(output_path),
            status="processing",
            period_start=data.start_at,
            period_end=data.end_at,
        )

        try:
            build_timelapse(
                image_paths=[Path(item.file_path) for item in snapshots],
                output_path=output_path,
                fps=data.fps,
                output_width=data.output_width,
                output_height=data.output_height,
            )

            record = timelapse_repository.update_status(
                db,
                record,
                status="completed",
                file_path=str(output_path),
            )

            try:
                cloud_service.upload_file(output_path)
            except Exception:
                pass

        except FFmpegError as exc:
            timelapse_repository.update_status(
                db,
                record,
                status="failed",
            )

            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc

        return record, len(snapshots)


timelapse_service = TimeLapseService()
