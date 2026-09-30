from pydantic import BaseModel, Field


class HighSpeedCaptureStart(BaseModel):
    camera_id: int = Field(ge=1)
    interval_seconds: float = Field(default=1.0, ge=0.5, le=60.0)
    duration_seconds: int = Field(default=900, ge=10, le=1800)


class HighSpeedCaptureStatus(BaseModel):
    camera_id: int | None = None
    running: bool = False
    state: str = "idle"
    interval_seconds: float | None = None
    duration_seconds: int | None = None
    expected_snapshots: int = 0
    captured_snapshots: int = 0
    failed_snapshots: int = 0
    started_at: str | None = None
    expected_end_at: str | None = None
    finished_at: str | None = None
    first_snapshot_at: str | None = None
    last_snapshot_at: str | None = None
    elapsed_seconds: float = 0.0
    remaining_seconds: float = 0.0
    progress_percent: float = 0.0
    last_error: str | None = None
