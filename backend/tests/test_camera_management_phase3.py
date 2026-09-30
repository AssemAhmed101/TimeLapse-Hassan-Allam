from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.repositories.camera_repository import CameraRepository
from app.schemas.camera import CameraCreate, CameraUpdate


def test_camera_crud_repository():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "phase3.db"

        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = CameraRepository()

        with Session() as db:
            camera = repo.create(
                db,
                CameraCreate(
                    name="Tower Test Camera",
                    provider="simulator",
                ),
            )

            assert camera.id is not None
            assert camera.is_enabled is True

            updated = repo.update(
                db,
                camera,
                CameraUpdate(name="Tower Test Camera Updated"),
            )

            assert updated.name == "Tower Test Camera Updated"

            disabled = repo.set_enabled(db, updated, False)
            assert disabled.is_enabled is False

            camera_id = disabled.id
            repo.delete(db, disabled)

            assert repo.get(db, camera_id) is None
        engine.dispose()
