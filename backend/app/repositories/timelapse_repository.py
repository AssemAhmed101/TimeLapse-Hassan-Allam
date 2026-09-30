from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.timelapse import TimeLapse


class TimeLapseRepository:
    def list(self, db: Session, camera_id: int | None = None) -> list[TimeLapse]:
        stmt = select(TimeLapse).order_by(TimeLapse.created_at.desc())

        if camera_id is not None:
            stmt = stmt.where(TimeLapse.camera_id == camera_id)

        return list(db.scalars(stmt).all())

    def library_page(
        self,
        db: Session,
        *,
        camera_id: int | None = None,
        status: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> tuple[list[TimeLapse], int]:
        filters = []

        if camera_id is not None:
            filters.append(TimeLapse.camera_id == camera_id)

        if status:
            filters.append(TimeLapse.status == status)

        if start_at is not None:
            filters.append(TimeLapse.created_at >= start_at)

        if end_at is not None:
            filters.append(TimeLapse.created_at <= end_at)

        count_stmt = select(func.count(TimeLapse.id))
        if filters:
            count_stmt = count_stmt.where(*filters)

        total = int(db.scalar(count_stmt) or 0)

        stmt = select(TimeLapse)
        if filters:
            stmt = stmt.where(*filters)

        stmt = (
            stmt.order_by(TimeLapse.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = list(db.scalars(stmt).all())
        return items, total

    def get(self, db: Session, timelapse_id: int) -> TimeLapse | None:
        return db.get(TimeLapse, timelapse_id)

    def create(
        self,
        db: Session,
        *,
        camera_id: int,
        file_path: str,
        status: str,
        period_start: datetime,
        period_end: datetime,
    ) -> TimeLapse:
        item = TimeLapse(
            camera_id=camera_id,
            file_path=file_path,
            status=status,
            period_start=period_start,
            period_end=period_end,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_status(
        self,
        db: Session,
        item: TimeLapse,
        status: str,
        file_path: str | None = None,
    ) -> TimeLapse:
        item.status = status

        if file_path is not None:
            item.file_path = file_path

        db.add(item)
        db.commit()
        db.refresh(item)
        return item


timelapse_repository = TimeLapseRepository()
