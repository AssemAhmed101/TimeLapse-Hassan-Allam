from datetime import time
from pathlib import Path
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.models.camera import Camera
from app.repositories.snapshot_policy_repository import SnapshotPolicyRepository
from app.schemas.snapshot_policy import SnapshotPolicyCreate


def test_snapshot_policy_defaults():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "phase4.db"

        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = SnapshotPolicyRepository()

        with Session() as db:
            camera = Camera(
                name="Tower Camera",
                provider="simulator",
            )
            db.add(camera)
            db.commit()
            db.refresh(camera)

            policy = repo.create(
                db,
                camera.id,
                SnapshotPolicyCreate(),
            )

            assert policy.camera_id == camera.id
            assert policy.enabled is True
            assert policy.interval_seconds == 21600
            assert policy.start_time == time(0, 0)
            assert policy.end_time == time(23, 59, 59)
            assert policy.retry_count == 3
        engine.dispose()



def test_snapshot_policy_custom_values():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "phase4_custom.db"

        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        repo = SnapshotPolicyRepository()

        with Session() as db:
            camera = Camera(
                name="Tower Camera",
                provider="simulator",
            )
            db.add(camera)
            db.commit()
            db.refresh(camera)

            policy = repo.create(
                db,
                camera.id,
                SnapshotPolicyCreate(
                    interval_seconds=60,
                    start_time=time(8, 0),
                    end_time=time(17, 0),
                    retry_count=2,
                    retry_delay_seconds=1,
                ),
            )

            assert policy.interval_seconds == 60
            assert policy.start_time == time(8, 0)
            assert policy.end_time == time(17, 0)
            assert policy.retry_count == 2
            assert policy.retry_delay_seconds == 1
        engine.dispose()
