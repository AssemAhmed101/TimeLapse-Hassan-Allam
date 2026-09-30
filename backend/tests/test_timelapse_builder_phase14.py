from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.models.camera import Camera
from app.models.snapshot import Snapshot
from app.services.timelapse_service import TimeLapseService


def test_timelapse_preview_counts_snapshots():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "builder.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        service = TimeLapseService()

        with Session() as db:
            camera = Camera(name="Tower Camera", provider="simulator")
            db.add(camera)
            db.commit()
            db.refresh(camera)

            now = datetime.now(timezone.utc)

            for index in range(50):
                db.add(
                    Snapshot(
                        camera_id=camera.id,
                        file_path=f"/tmp/frame_{index}.jpg",
                        captured_at=now + timedelta(seconds=index),
                    )
                )

            db.commit()

            result = service.preview(
                db=db,
                camera_id=camera.id,
                start_at=now - timedelta(seconds=1),
                end_at=now + timedelta(seconds=60),
                fps=25,
            )

            assert result["snapshot_count"] == 50
            assert result["can_generate"] is True
            assert result["estimated_duration_seconds"] == 2.0
        engine.dispose()



def test_timelapse_preview_requires_two_snapshots():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "builder_min.db"
        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        service = TimeLapseService()

        with Session() as db:
            camera = Camera(name="Tower Camera", provider="simulator")
            db.add(camera)
            db.commit()
            db.refresh(camera)

            now = datetime.now(timezone.utc)

            db.add(
                Snapshot(
                    camera_id=camera.id,
                    file_path="/tmp/only.jpg",
                    captured_at=now,
                )
            )
            db.commit()

            result = service.preview(
                db=db,
                camera_id=camera.id,
                start_at=now - timedelta(seconds=1),
                end_at=now + timedelta(seconds=1),
                fps=25,
            )

            assert result["snapshot_count"] == 1
            assert result["can_generate"] is False
        engine.dispose()
