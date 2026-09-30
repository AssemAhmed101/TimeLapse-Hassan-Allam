from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.snapshot_policy import (
    SnapshotEngineRunResponse,
    SnapshotPolicyRead,
    SnapshotPolicyUpdate,
)
from app.services.snapshot_engine import snapshot_engine
from app.services.snapshot_policy_service import snapshot_policy_service

router = APIRouter()


@router.get(
    "/cameras/{camera_id}/policy",
    response_model=SnapshotPolicyRead,
)
def get_snapshot_policy(
    camera_id: int,
    db: Session = Depends(get_db),
):
    return snapshot_policy_service.get_or_create(db, camera_id)


@router.patch(
    "/cameras/{camera_id}/policy",
    response_model=SnapshotPolicyRead,
)
def update_snapshot_policy(
    camera_id: int,
    data: SnapshotPolicyUpdate,
    db: Session = Depends(get_db),
):
    return snapshot_policy_service.update(db, camera_id, data)


@router.post(
    "/cameras/{camera_id}/run-once",
    response_model=SnapshotEngineRunResponse,
)
def run_snapshot_engine_once(
    camera_id: int,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return snapshot_engine.run_once(
        db=db,
        camera_id=camera_id,
        force=force,
    )
