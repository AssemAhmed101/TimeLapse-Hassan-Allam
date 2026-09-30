from pydantic import BaseModel, Field


class StorageCategoryStats(BaseModel):
    file_count: int
    total_bytes: int
    total_mb: float
    total_gb: float


class StorageDiskStats(BaseModel):
    total_bytes: int
    used_bytes: int
    free_bytes: int
    free_gb: float
    usage_percent: float
    warning: bool
    warning_level: str


class StorageForecast(BaseModel):
    configured_capacity_gb: float
    camera_count: int
    captures_per_camera_per_day: int
    total_images_per_day: int
    annual_images: int
    assumed_image_size_mb: float
    estimated_annual_gb: float
    estimated_capacity_years: float


class StorageStatusResponse(BaseModel):
    root_path: str
    snapshots: StorageCategoryStats
    timelapses: StorageCategoryStats
    disk: StorageDiskStats
    forecast: StorageForecast


class StorageCleanupRequest(BaseModel):
    dry_run: bool = True
    snapshot_retention_days: int | None = Field(default=None, ge=0, le=3650)
    timelapse_retention_days: int | None = Field(default=None, ge=0, le=3650)


class StorageCleanupResult(BaseModel):
    dry_run: bool
    scanned_files: int
    matched_files: int
    deleted_files: int
    freed_bytes: int
    freed_mb: float
    errors: list[str]
