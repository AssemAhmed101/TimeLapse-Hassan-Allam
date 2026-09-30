from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.cloud.base import CloudStorageError
from app.schemas.cloud import (
    CloudStatusResponse,
    CloudSyncResponse,
    CloudUploadResponse,
)
from app.services.cloud_service import cloud_service

router = APIRouter()


@router.get("/status", response_model=CloudStatusResponse)
def cloud_status():
    return cloud_service.status()


@router.post("/upload", response_model=CloudUploadResponse)
def upload_file(path: str = Query(...)):
    try:
        return cloud_service.upload_file(Path(path))
    except CloudStorageError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/sync", response_model=CloudSyncResponse)
def sync_storage():
    return cloud_service.sync_storage()
