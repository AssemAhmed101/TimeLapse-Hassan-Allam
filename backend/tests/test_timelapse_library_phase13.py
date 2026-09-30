from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.models.camera import Camera
from app.models.timelapse import TimeLapse
from app.repositories.timelapse_repository import TimeLapseRepository


def test_timelapse_library_pagination_and_filter():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "timelapse_library.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = TimeLapseRepository()

        with Session() as db:
            camera1 = Camera(name="Camera 1", provider="simulator")
            camera2 = Camera(name="Camera 2", provider="simulator")
            db.add_all([camera1, camera2])
            db.commit()
            db.refresh(camera1)
            db.refresh(camera2)

            now = datetime.now(timezone.utc)

            for index in range(4):
                db.add(
                    TimeLapse(
                        camera_id=camera1.id,
                        file_path=f"/tmp/c1_{index}.mp4",
                        status="completed",
                        period_start=now - timedelta(hours=1),
                        period_end=now,
                        created_at=now + timedelta(minutes=index),
                    )
                )

            db.add(
                TimeLapse(
                    camera_id=camera2.id,
                    file_path="/tmp/c2.mp4",
                    status="failed",
                    period_start=now - timedelta(hours=1),
                    period_end=now,
                    created_at=now,
                )
            )

            db.commit()

            items, total = repo.library_page(
                db,
                camera_id=camera1.id,
                status="completed",
                page=1,
                page_size=2,
            )

            assert total == 4
            assert len(items) == 2
            assert all(item.camera_id == camera1.id for item in items)
            assert all(item.status == "completed" for item in items)
        engine.dispose()



def test_timelapse_library_date_filter():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "timelapse_dates.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = TimeLapseRepository()

        with Session() as db:
            camera = Camera(name="Camera", provider="simulator")
            db.add(camera)
            db.commit()
            db.refresh(camera)

            now = datetime.now(timezone.utc)

            db.add_all([
                TimeLapse(
                    camera_id=camera.id,
                    file_path="/tmp/old.mp4",
                    status="completed",
                    period_start=now - timedelta(days=6),
                    period_end=now - timedelta(days=5),
                    created_at=now - timedelta(days=5),
                ),
                TimeLapse(
                    camera_id=camera.id,
                    file_path="/tmp/new.mp4",
                    status="completed",
                    period_start=now - timedelta(hours=1),
                    period_end=now,
                    created_at=now,
                ),
            ])
            db.commit()

            items, total = repo.library_page(
                db,
                camera_id=camera.id,
                start_at=now - timedelta(days=1),
                end_at=now + timedelta(minutes=1),
                page=1,
                page_size=10,
            )

            assert total == 1
            assert len(items) == 1
            assert items[0].file_path.endswith("new.mp4")
        engine.dispose()
