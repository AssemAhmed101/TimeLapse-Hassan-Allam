from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeLapseCreateRequest(BaseModel):
    camera_id: int
    start_at: datetime
    end_at: datetime
    fps: int = Field(default=25, ge=1, le=60)
    output_width: int | None = Field(default=None, ge=320, le=7680)
    output_height: int | None = Field(default=None, ge=240, le=4320)


class TimeLapseRead(BaseModel):
    id: int
    camera_id: int
    file_path: str
    status: str
    period_start: datetime | None
    period_end: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeLapseLibraryItem(BaseModel):
    id: int
    camera_id: int
    status: str
    period_start: datetime | None
    period_end: datetime | None
    created_at: datetime
    filename: str
    video_url: str | None
    download_url: str | None


class TimeLapseLibraryResponse(BaseModel):
    items: list[TimeLapseLibraryItem]
    total: int
    page: int
    page_size: int
    pages: int


class FFmpegStatusResponse(BaseModel):
    available: bool
    ffmpeg_path: str | None = None
    ffprobe_path: str | None = None


class TimeLapseGenerationResponse(BaseModel):
    success: bool
    timelapse: TimeLapseRead
    snapshot_count: int


class TimeLapsePreviewRequest(BaseModel):
    camera_id: int
    start_at: datetime
    end_at: datetime
    fps: int = Field(default=25, ge=1, le=60)


class TimeLapsePreviewResponse(BaseModel):
    camera_id: int
    snapshot_count: int
    can_generate: bool
    fps: int
    estimated_duration_seconds: float
    first_snapshot_at: datetime | None = None
    last_snapshot_at: datetime | None = None
