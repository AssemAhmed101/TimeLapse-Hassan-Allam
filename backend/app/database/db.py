from app.database.base import Base
from app.database.session import engine

from app.models.camera import Camera  # noqa: F401
from app.models.snapshot import Snapshot  # noqa: F401
from app.models.timelapse import TimeLapse  # noqa: F401
from app.models.system_setting import SystemSetting  # noqa: F401
from app.models.snapshot_policy import SnapshotPolicy  # noqa: F401
from app.models.user import User  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
