from datetime import time

from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SnapshotPolicy(Base):
    __tablename__ = "snapshot_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    camera_id: Mapped[int] = mapped_column(
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=21600)
    start_time: Mapped[time] = mapped_column(Time, nullable=False, default=time(0, 0))
    end_time: Mapped[time] = mapped_column(Time, nullable=False, default=time(23, 59, 59))
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    camera = relationship("Camera", back_populates="snapshot_policy")
