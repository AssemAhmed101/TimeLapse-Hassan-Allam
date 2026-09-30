from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.snapshot_policy import SnapshotPolicy
from app.repositories.snapshot_policy_repository import snapshot_policy_repository
from app.schemas.snapshot_policy import SnapshotPolicyCreate, SnapshotPolicyUpdate
from app.services.camera_service import camera_service


class SnapshotPolicyService:
    def get_or_create(self, db: Session, camera_id: int) -> SnapshotPolicy:
        camera_service.get_camera(db, camera_id)

        policy = snapshot_policy_repository.get_by_camera(db, camera_id)
        if policy is None:
            policy = snapshot_policy_repository.create(db, camera_id)

        return policy

    def update(
        self,
        db: Session,
        camera_id: int,
        data: SnapshotPolicyUpdate,
    ) -> SnapshotPolicy:
        policy = self.get_or_create(db, camera_id)

        start_time = data.start_time if data.start_time is not None else policy.start_time
        end_time = data.end_time if data.end_time is not None else policy.end_time

        if start_time == end_time:
            raise HTTPException(
                status_code=422,
                detail="start_time and end_time cannot be the same",
            )

        return snapshot_policy_repository.update(db, policy, data)


snapshot_policy_service = SnapshotPolicyService()
