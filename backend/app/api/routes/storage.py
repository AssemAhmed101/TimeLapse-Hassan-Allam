from fastapi import APIRouter

from app.schemas.storage import (
    StorageCleanupRequest,
    StorageCleanupResult,
    StorageStatusResponse,
)
from app.services.storage_service import storage_service

router = APIRouter()


@router.get("/status", response_model=StorageStatusResponse)
def storage_status():
    return storage_service.status()


@router.post("/cleanup", response_model=StorageCleanupResult)
def cleanup_storage(data: StorageCleanupRequest):
    return storage_service.cleanup(
        dry_run=data.dry_run,
        snapshot_retention_days=data.snapshot_retention_days,
        timelapse_retention_days=data.timelapse_retention_days,
    )
