from fastapi import APIRouter, Depends, Query

from app.api.deps import require_roles
from app.services.monitoring_service import monitoring_service

router = APIRouter()


@router.get("/health")
def detailed_health():
    return monitoring_service.health()


@router.get("/logs")
def recent_logs(
    limit: int = Query(default=100, ge=1, le=500),
    _=Depends(require_roles("admin", "operator")),
):
    return monitoring_service.read_logs(limit=limit)
