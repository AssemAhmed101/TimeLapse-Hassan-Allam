from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database.session import get_db
from app.schemas.camera import (
    CameraCreate,
    CameraDeleteResponse,
    CameraRead,
    CameraStatusResponse,
    CameraToggleResponse,
    CameraUpdate,
)
from app.services.camera_service import camera_service

router = APIRouter()


@router.get("/", response_model=list[CameraRead])
def list_cameras(db: Session = Depends(get_db)):
    return camera_service.list_cameras(db)


@router.post("/", response_model=CameraRead, status_code=201)
def create_camera(
    data: CameraCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return camera_service.create_camera(db, data)


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
):
    return camera_service.get_camera(db, camera_id)


@router.patch("/{camera_id}", response_model=CameraRead)
def update_camera(
    camera_id: int,
    data: CameraUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return camera_service.update_camera(db, camera_id, data)


@router.delete("/{camera_id}", response_model=CameraDeleteResponse)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    camera_service.delete_camera(db, camera_id)

    return CameraDeleteResponse(
        success=True,
        deleted_camera_id=camera_id,
    )


@router.post("/{camera_id}/enable", response_model=CameraToggleResponse)
def enable_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    camera = camera_service.set_enabled(db, camera_id, True)

    return CameraToggleResponse(
        id=camera.id,
        is_enabled=camera.is_enabled,
        message="Camera enabled",
    )


@router.post("/{camera_id}/disable", response_model=CameraToggleResponse)
def disable_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    camera = camera_service.set_enabled(db, camera_id, False)

    return CameraToggleResponse(
        id=camera.id,
        is_enabled=camera.is_enabled,
        message="Camera disabled",
    )


@router.post("/{camera_id}/test-connection", response_model=CameraStatusResponse)
def test_camera_connection(
    camera_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return camera_service.test_connection(db, camera_id)
