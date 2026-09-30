from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CameraProviderName = Literal["simulator", "hikvision", "hikvision_nvr"]
CameraScheme = Literal["http", "https"]


class CameraCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    provider: CameraProviderName = "simulator"

    host: str | None = None
    username: str | None = None
    password: str | None = None

    scheme: CameraScheme = "http"
    port: int | None = Field(default=None, ge=1, le=65535)
    channel: int = Field(default=1, ge=1, le=256)
    ptz_preset_id: int | None = Field(default=None, ge=1, le=300)
    ptz_settle_seconds: int = Field(default=15, ge=0, le=120)

    is_enabled: bool = True


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    provider: CameraProviderName | None = None

    host: str | None = None
    username: str | None = None
    password: str | None = None

    scheme: CameraScheme | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    channel: int | None = Field(default=None, ge=1, le=256)
    ptz_preset_id: int | None = Field(default=None, ge=1, le=300)
    ptz_settle_seconds: int | None = Field(default=None, ge=0, le=120)

    is_enabled: bool | None = None


class CameraRead(BaseModel):
    id: int
    name: str
    provider: str
    host: str | None
    username: str | None

    scheme: str
    port: int | None
    channel: int
    ptz_preset_id: int | None
    ptz_settle_seconds: int

    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CameraStatusResponse(BaseModel):
    camera_id: int
    provider: str
    status: str
    message: str
    status_code: int | None = None


class CameraToggleResponse(BaseModel):
    id: int
    is_enabled: bool
    message: str


class CameraDeleteResponse(BaseModel):
    success: bool
    deleted_camera_id: int
