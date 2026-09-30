from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CameraRepository:
    def list(self, db: Session) -> list[Camera]:
        return list(db.scalars(select(Camera).order_by(Camera.id)).all())

    def get(self, db: Session, camera_id: int) -> Camera | None:
        return db.get(Camera, camera_id)

    def create(self, db: Session, data: CameraCreate) -> Camera:
        camera = Camera(**data.model_dump())
        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera

    def update(self, db: Session, camera: Camera, data: CameraUpdate) -> Camera:
        updates = data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(camera, field, value)

        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera

    def set_enabled(self, db: Session, camera: Camera, enabled: bool) -> Camera:
        camera.is_enabled = enabled
        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera

    def delete(self, db: Session, camera: Camera) -> None:
        db.delete(camera)
        db.commit()


camera_repository = CameraRepository()
