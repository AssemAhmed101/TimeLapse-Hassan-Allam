from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_media_user, get_current_user, require_roles
from app.database.session import get_db
from app.schemas.timelapse import (
    FFmpegStatusResponse,
    TimeLapseCreateRequest,
    TimeLapseGenerationResponse,
    TimeLapseLibraryResponse,
    TimeLapsePreviewRequest,
    TimeLapsePreviewResponse,
    TimeLapseRead,
)
from app.services.timelapse_service import timelapse_service
from app.utils.ffmpeg import get_ffmpeg_path, get_ffprobe_path

router = APIRouter()


@router.get("/ffmpeg-status", response_model=FFmpegStatusResponse)
def ffmpeg_status(_=Depends(get_current_user)):
    ffmpeg_path = get_ffmpeg_path()
    ffprobe_path = get_ffprobe_path()

    return FFmpegStatusResponse(
        available=ffmpeg_path is not None,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )


@router.post("/preview", response_model=TimeLapsePreviewResponse)
def preview_timelapse(
    data: TimeLapsePreviewRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return timelapse_service.preview(
        db=db,
        camera_id=data.camera_id,
        start_at=data.start_at,
        end_at=data.end_at,
        fps=data.fps,
    )


@router.get("/library", response_model=TimeLapseLibraryResponse)
def timelapse_library(
    camera_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return timelapse_service.library(
        db,
        camera_id=camera_id,
        status=status,
        start_at=start_at,
        end_at=end_at,
        page=page,
        page_size=page_size,
    )


@router.get("/{timelapse_id}/video")
def timelapse_video(
    timelapse_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_media_user),
):
    path = timelapse_service.get_video_file(db, timelapse_id)
    return FileResponse(
        path,
        media_type="video/mp4",
        filename=path.name,
        content_disposition_type="inline",
    )


@router.get("/{timelapse_id}/download")
def timelapse_download(
    timelapse_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_media_user),
):
    path = timelapse_service.get_video_file(db, timelapse_id)
    return FileResponse(
        path,
        media_type="video/mp4",
        filename=path.name,
        content_disposition_type="attachment",
    )


@router.get("/", response_model=list[TimeLapseRead])
def list_timelapses(
    camera_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return timelapse_service.list(db, camera_id)


@router.get("/{timelapse_id}", response_model=TimeLapseRead)
def get_timelapse(
    timelapse_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return timelapse_service.get(db, timelapse_id)


@router.post(
    "/generate",
    response_model=TimeLapseGenerationResponse,
    status_code=201,
)
def generate_timelapse(
    data: TimeLapseCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    record, snapshot_count = timelapse_service.generate(db, data)

    return TimeLapseGenerationResponse(
        success=True,
        timelapse=TimeLapseRead.model_validate(record),
        snapshot_count=snapshot_count,
    )
