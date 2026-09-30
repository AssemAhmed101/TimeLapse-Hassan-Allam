from datetime import datetime
from math import ceil
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.snapshot import Snapshot
from app.repositories.snapshot_repository import snapshot_repository
from app.services.camera_service import camera_service
from app.services.cloud_service import cloud_service


class SnapshotService:
    def list_snapshots(
        self,
        db: Session,
        camera_id: int | None = None,
    ) -> list[Snapshot]:
        return snapshot_repository.list(db, camera_id)

    def get_snapshot(self, db: Session, snapshot_id: int) -> Snapshot:
        snapshot = snapshot_repository.get(db, snapshot_id)
        if snapshot is None:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        return snapshot

    def get_snapshot_file(self, db: Session, snapshot_id: int) -> Path:
        snapshot = self.get_snapshot(db, snapshot_id)
        path = Path(snapshot.file_path).resolve()

        if not path.exists() or not path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Snapshot file is missing from storage",
            )

        return path

    def archive(
        self,
        db: Session,
        *,
        camera_id: int | None,
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

        items, total = snapshot_repository.archive_page(
            db,
            camera_id=camera_id,
            start_at=start_at,
            end_at=end_at,
            page=page,
            page_size=page_size,
        )

        pages = ceil(total / page_size) if total else 0

        return {
            "items": [
                {
                    "id": item.id,
                    "camera_id": item.camera_id,
                    "captured_at": item.captured_at,
                    "image_url": f"/api/v1/snapshots/{item.id}/image",
                    "download_url": f"/api/v1/snapshots/{item.id}/download",
                    "filename": Path(item.file_path).name,
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    def capture(self, db: Session, camera_id: int) -> Snapshot:
        camera = camera_service.get_camera(db, camera_id)

        if not camera.is_enabled:
            from fastapi import HTTPException
            raise HTTPException(status_code=409, detail="Camera is disabled")

        provider = camera_service.build_provider(camera)
        file_path = provider.capture_snapshot()

        snapshot = snapshot_repository.create(
            db=db,
            camera_id=camera.id,
            file_path=str(file_path),
        )

        try:
            cloud_service.upload_file(file_path)
        except Exception:
            pass

        return snapshot


snapshot_service = SnapshotService()
