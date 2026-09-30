from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SnapshotPolicyCreate(BaseModel):
    enabled: bool = True
    interval_seconds: int = Field(default=21600, ge=10, le=86400)
    start_time: time = time(0, 0)
    end_time: time = time(23, 59, 59)
    retry_count: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=2, ge=0, le=300)

    @model_validator(mode="after")
    def validate_window(self):
        if self.start_time == self.end_time:
            raise ValueError("start_time and end_time cannot be the same")
        return self


class SnapshotPolicyUpdate(BaseModel):
    enabled: bool | None = None
    interval_seconds: int | None = Field(default=None, ge=10, le=86400)
    start_time: time | None = None
    end_time: time | None = None
    retry_count: int | None = Field(default=None, ge=0, le=10)
    retry_delay_seconds: int | None = Field(default=None, ge=0, le=300)


class SnapshotPolicyRead(BaseModel):
    id: int
    camera_id: int
    enabled: bool
    interval_seconds: int
    start_time: time
    end_time: time
    retry_count: int
    retry_delay_seconds: int

    model_config = ConfigDict(from_attributes=True)


class SnapshotEngineRunResponse(BaseModel):
    camera_id: int
    status: str
    reason: str | None = None
    snapshot_id: int | None = None
    file_path: str | None = None
