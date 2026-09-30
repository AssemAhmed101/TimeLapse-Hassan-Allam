from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SnapshotRead(BaseModel):
    id: int
    camera_id: int
    file_path: str
    captured_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SnapshotCreateResponse(BaseModel):
    success: bool
    snapshot: SnapshotRead


class SnapshotArchiveItem(BaseModel):
    id: int
    camera_id: int
    captured_at: datetime
    image_url: str
    download_url: str
    filename: str


class SnapshotArchiveResponse(BaseModel):
    items: list[SnapshotArchiveItem]
    total: int
    page: int
    page_size: int
    pages: int
