from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.models.camera import Camera
from app.models.snapshot import Snapshot


def test_camera_and_snapshot_relationship():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        with Session() as db:
            camera = Camera(name="Test Camera", provider="simulator")
            db.add(camera)
            db.commit()
            db.refresh(camera)

            snapshot = Snapshot(
                camera_id=camera.id,
                file_path="storage/snapshots/test.jpg",
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)

            assert snapshot.camera_id == camera.id
            assert camera.id is not None
        engine.dispose()
