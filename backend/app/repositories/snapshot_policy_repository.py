from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.snapshot_policy import SnapshotPolicy
from app.schemas.snapshot_policy import SnapshotPolicyCreate, SnapshotPolicyUpdate


class SnapshotPolicyRepository:
    def get_by_camera(self, db: Session, camera_id: int) -> SnapshotPolicy | None:
        stmt = select(SnapshotPolicy).where(SnapshotPolicy.camera_id == camera_id)
        return db.scalar(stmt)

    def create(
        self,
        db: Session,
        camera_id: int,
        data: SnapshotPolicyCreate | None = None,
    ) -> SnapshotPolicy:
        data = data or SnapshotPolicyCreate()

        policy = SnapshotPolicy(
            camera_id=camera_id,
            **data.model_dump(),
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def update(
        self,
        db: Session,
        policy: SnapshotPolicy,
        data: SnapshotPolicyUpdate,
    ) -> SnapshotPolicy:
        updates = data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(policy, field, value)

        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy


snapshot_policy_repository = SnapshotPolicyRepository()
