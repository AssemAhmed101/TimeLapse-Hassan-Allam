from pydantic import BaseModel


class CloudStatusResponse(BaseModel):
    provider: str
    configured: bool
    bucket: str
    prefix: str


class CloudUploadResponse(BaseModel):
    success: bool
    local_path: str
    object_key: str
    cloud_url: str


class CloudSyncResponse(BaseModel):
    scanned_files: int
    uploaded_files: int
    skipped_files: int
    failed_files: int
    errors: list[str]
