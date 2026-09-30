from fastapi import APIRouter

from app.services.scheduler_service import scheduler_service

router = APIRouter()


@router.get("/status")
def scheduler_status():
    return scheduler_service.status()


@router.post("/run-cycle")
def run_scheduler_cycle():
    return scheduler_service.run_snapshot_cycle()
