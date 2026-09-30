from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.schemas.high_speed_capture import HighSpeedCaptureStart, HighSpeedCaptureStatus
from app.services.high_speed_capture_service import high_speed_capture_service

router = APIRouter()


@router.post("/start", response_model=HighSpeedCaptureStatus)
def start_high_speed_capture(
    data: HighSpeedCaptureStart,
    _=Depends(require_roles("admin", "operator")),
):
    return high_speed_capture_service.start(
        camera_id=data.camera_id,
        interval_seconds=data.interval_seconds,
        duration_seconds=data.duration_seconds,
    )


@router.get("/{camera_id}/status", response_model=HighSpeedCaptureStatus)
def high_speed_capture_status(
    camera_id: int,
    _=Depends(require_roles("admin", "operator", "viewer")),
):
    return high_speed_capture_service.status(camera_id)


@router.post("/{camera_id}/stop", response_model=HighSpeedCaptureStatus)
def stop_high_speed_capture(
    camera_id: int,
    _=Depends(require_roles("admin", "operator")),
):
    return high_speed_capture_service.stop(camera_id)
