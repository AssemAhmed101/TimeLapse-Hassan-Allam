from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.models.camera import Camera
from app.models.snapshot import Snapshot
from app.repositories.snapshot_repository import SnapshotRepository


def test_snapshot_archive_pagination_and_filter():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "archive.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = SnapshotRepository()

        with Session() as db:
            camera1 = Camera(name="Camera 1", provider="simulator")
            camera2 = Camera(name="Camera 2", provider="simulator")
            db.add_all([camera1, camera2])
            db.commit()
            db.refresh(camera1)
            db.refresh(camera2)

            base = datetime.now(timezone.utc)

            for index in range(5):
                db.add(
                    Snapshot(
                        camera_id=camera1.id,
                        file_path=f"/tmp/c1_{index}.jpg",
                        captured_at=base + timedelta(minutes=index),
                    )
                )

            for index in range(2):
                db.add(
                    Snapshot(
                        camera_id=camera2.id,
                        file_path=f"/tmp/c2_{index}.jpg",
                        captured_at=base + timedelta(minutes=index),
                    )
                )

            db.commit()

            items, total = repo.archive_page(
                db,
                camera_id=camera1.id,
                page=1,
                page_size=2,
            )

            assert total == 5
            assert len(items) == 2
            assert all(item.camera_id == camera1.id for item in items)
        engine.dispose()



def test_snapshot_archive_date_filter():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "archive_dates.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = SnapshotRepository()

        with Session() as db:
            camera = Camera(name="Camera", provider="simulator")
            db.add(camera)
            db.commit()
            db.refresh(camera)

            now = datetime.now(timezone.utc)

            db.add_all([
                Snapshot(
                    camera_id=camera.id,
                    file_path="/tmp/old.jpg",
                    captured_at=now - timedelta(days=5),
                ),
                Snapshot(
                    camera_id=camera.id,
                    file_path="/tmp/new.jpg",
                    captured_at=now,
                ),
            ])
            db.commit()

            items, total = repo.archive_page(
                db,
                camera_id=camera.id,
                start_at=now - timedelta(days=1),
                end_at=now + timedelta(minutes=1),
                page=1,
                page_size=10,
            )

            assert total == 1
            assert len(items) == 1
            assert items[0].file_path.endswith("new.jpg")
        engine.dispose()
