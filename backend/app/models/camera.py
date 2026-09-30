from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="simulator")

    host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    scheme: Mapped[str] = mapped_column(String(10), nullable=False, default="http")
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ptz_preset_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ptz_settle_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=15)

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    snapshots = relationship(
        "Snapshot",
        back_populates="camera",
        cascade="all, delete-orphan",
    )
    timelapses = relationship(
        "TimeLapse",
        back_populates="camera",
        cascade="all, delete-orphan",
    )
    snapshot_policy = relationship(
        "SnapshotPolicy",
        back_populates="camera",
        cascade="all, delete-orphan",
        uselist=False,
    )
