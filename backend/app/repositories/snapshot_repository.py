from __future__ import annotations

from datetime import datetime
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.snapshot import Snapshot


class SnapshotRepository:
    def list(self, db: Session, camera_id: int | None = None) -> list[Snapshot]:
        stmt = select(Snapshot).order_by(Snapshot.captured_at.desc())

        if camera_id is not None:
            stmt = stmt.where(Snapshot.camera_id == camera_id)

        return list(db.scalars(stmt).all())

    def list_between(
        self,
        db: Session,
        camera_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Snapshot]:
        stmt = (
            select(Snapshot)
            .where(
                Snapshot.camera_id == camera_id,
                Snapshot.captured_at >= start_at,
                Snapshot.captured_at <= end_at,
            )
            .order_by(Snapshot.captured_at.asc())
        )

        return list(db.scalars(stmt).all())

    def archive_page(
        self,
        db: Session,
        *,
        camera_id: int | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> tuple[list[Snapshot], int]:
        filters = []

        if camera_id is not None:
            filters.append(Snapshot.camera_id == camera_id)
        if start_at is not None:
            filters.append(Snapshot.captured_at >= start_at)
        if end_at is not None:
            filters.append(Snapshot.captured_at <= end_at)

        count_stmt = select(func.count(Snapshot.id))
        if filters:
            count_stmt = count_stmt.where(*filters)

        total = int(db.scalar(count_stmt) or 0)

        stmt = select(Snapshot)
        if filters:
            stmt = stmt.where(*filters)

        stmt = (
            stmt.order_by(Snapshot.captured_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = list(db.scalars(stmt).all())
        return items, total

    def get(self, db: Session, snapshot_id: int) -> Snapshot | None:
        return db.get(Snapshot, snapshot_id)

    def get_last_for_camera(self, db: Session, camera_id: int) -> Snapshot | None:
        stmt = (
            select(Snapshot)
            .where(Snapshot.camera_id == camera_id)
            .order_by(Snapshot.captured_at.desc())
            .limit(1)
        )

        return db.scalar(stmt)

    def create(self, db: Session, camera_id: int, file_path: str) -> Snapshot:
        snapshot = Snapshot(
            camera_id=camera_id,
            file_path=file_path,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot


snapshot_repository = SnapshotRepository()
