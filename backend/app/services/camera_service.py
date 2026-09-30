from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.camera.hikvision import HikvisionCamera
from app.camera.hikvision_nvr import HikvisionNVR
from app.camera.simulator import SimulatorCamera
from app.camera.base import CameraConnectionError
from app.models.camera import Camera
from app.repositories.camera_repository import camera_repository
from app.schemas.camera import CameraCreate, CameraUpdate
from app.services.storage_service import storage_service


SUPPORTED_PROVIDERS = {"simulator", "hikvision", "hikvision_nvr"}


class CameraService:
    def list_cameras(self, db: Session) -> list[Camera]:
        return camera_repository.list(db)

    def get_camera(self, db: Session, camera_id: int) -> Camera:
        camera = camera_repository.get(db, camera_id)
        if camera is None:
            raise HTTPException(status_code=404, detail="Camera not found")
        return camera

    def create_camera(self, db: Session, data: CameraCreate) -> Camera:
        self._validate_configuration(data.model_dump())
        return camera_repository.create(db, data)

    def update_camera(
        self,
        db: Session,
        camera_id: int,
        data: CameraUpdate,
    ) -> Camera:
        camera = self.get_camera(db, camera_id)

        current = {
            "provider": camera.provider,
            "host": camera.host,
            "username": camera.username,
            "password": camera.password,
            "scheme": camera.scheme,
            "port": camera.port,
            "channel": camera.channel,
            "ptz_preset_id": camera.ptz_preset_id,
            "ptz_settle_seconds": camera.ptz_settle_seconds,
        }
        current.update(data.model_dump(exclude_unset=True))

        self._validate_configuration(current)
        return camera_repository.update(db, camera, data)

    def delete_camera(self, db: Session, camera_id: int) -> None:
        camera = self.get_camera(db, camera_id)
        camera_repository.delete(db, camera)

    def set_enabled(
        self,
        db: Session,
        camera_id: int,
        enabled: bool,
    ) -> Camera:
        camera = self.get_camera(db, camera_id)
        return camera_repository.set_enabled(db, camera, enabled)

    def build_provider(self, camera: Camera):
        output_dir = storage_service.camera_snapshot_dir(camera.id)

        if camera.provider == "simulator":
            return SimulatorCamera(output_dir)

        if camera.provider == "hikvision":
            return HikvisionCamera(
                host=camera.host or "",
                username=camera.username or "",
                password=camera.password or "",
                output_dir=output_dir,
                channel=camera.channel,
                scheme=camera.scheme,
                port=camera.port,
                ptz_preset_id=camera.ptz_preset_id,
                ptz_settle_seconds=camera.ptz_settle_seconds,
            )

        if camera.provider == "hikvision_nvr":
            return HikvisionNVR(
                host=camera.host or "",
                username=camera.username or "",
                password=camera.password or "",
                output_dir=output_dir,
                channel=camera.channel,
                scheme=camera.scheme,
                port=camera.port,
                ptz_preset_id=camera.ptz_preset_id,
                ptz_settle_seconds=camera.ptz_settle_seconds,
            )

        raise HTTPException(
            status_code=501,
            detail=f"Camera provider '{camera.provider}' is not implemented",
        )

    def test_connection(self, db: Session, camera_id: int) -> dict:
        camera = self.get_camera(db, camera_id)

        if not camera.is_enabled:
            return {
                "camera_id": camera.id,
                "provider": camera.provider,
                "status": "disabled",
                "message": "Camera is disabled",
                "status_code": None,
            }

        provider = self.build_provider(camera)

        try:
            result = provider.test_connection()
        except CameraConnectionError as exc:
            return {
                "camera_id": camera.id,
                "provider": camera.provider,
                "status": "offline",
                "message": str(exc),
                "status_code": None,
            }

        return {
            "camera_id": camera.id,
            "provider": camera.provider,
            "status": "connected" if result.get("connected") else "offline",
            "message": result.get("message", ""),
            "status_code": result.get("status_code"),
        }

    @staticmethod
    def _validate_configuration(data: dict) -> None:
        provider = data.get("provider")

        if provider not in SUPPORTED_PROVIDERS:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported camera provider: {provider}",
            )

        if provider in {"hikvision", "hikvision_nvr"}:
            if not data.get("host"):
                raise HTTPException(
                    status_code=422,
                    detail="host is required for Hikvision providers",
                )
            if not data.get("username"):
                raise HTTPException(
                    status_code=422,
                    detail="username is required for Hikvision providers",
                )
            if not data.get("password"):
                raise HTTPException(
                    status_code=422,
                    detail="password is required for Hikvision providers",
                )


camera_service = CameraService()
