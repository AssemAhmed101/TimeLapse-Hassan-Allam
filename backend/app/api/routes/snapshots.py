from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_media_user, get_current_user, require_roles
from app.database.session import get_db
from app.schemas.snapshot import (
    SnapshotArchiveResponse,
    SnapshotCreateResponse,
    SnapshotRead,
)
from app.services.snapshot_service import snapshot_service

router = APIRouter()


@router.get("/", response_model=list[SnapshotRead])
def list_snapshots(
    camera_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return snapshot_service.list_snapshots(db, camera_id)


@router.get("/archive", response_model=SnapshotArchiveResponse)
def snapshot_archive(
    camera_id: int | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return snapshot_service.archive(
        db,
        camera_id=camera_id,
        start_at=start_at,
        end_at=end_at,
        page=page,
        page_size=page_size,
    )


@router.get("/{snapshot_id}/image")
def snapshot_image(
    snapshot_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_media_user),
):
    path = snapshot_service.get_snapshot_file(db, snapshot_id)
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=path.name,
        content_disposition_type="inline",
    )


@router.get("/{snapshot_id}/download")
def snapshot_download(
    snapshot_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_media_user),
):
    path = snapshot_service.get_snapshot_file(db, snapshot_id)
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=path.name,
        content_disposition_type="attachment",
    )


@router.post("/{camera_id}", response_model=SnapshotCreateResponse, status_code=201)
def capture_snapshot(camera_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin", "operator"))):
    snapshot = snapshot_service.capture(db, camera_id)

    return SnapshotCreateResponse(
        success=True,
        snapshot=SnapshotRead.model_validate(snapshot),
    )
