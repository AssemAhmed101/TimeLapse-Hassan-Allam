from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.routes import (
    auth,
    cameras,
    cloud,
    health,
    high_speed_capture,
    monitoring,
    scheduler,
    settings as settings_routes,
    snapshot_engine,
    snapshots,
    storage,
    timelapses,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(high_speed_capture.router, prefix="/high-speed-capture", tags=["High-Speed Capture"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"], dependencies=[Depends(get_current_user)])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

protected = [Depends(get_current_user)]
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"], dependencies=protected)
api_router.include_router(snapshots.router, prefix="/snapshots", tags=["Snapshots"])
api_router.include_router(snapshot_engine.router, prefix="/snapshot-engine", tags=["Snapshot Engine"], dependencies=protected)
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"], dependencies=protected)
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"], dependencies=protected)
api_router.include_router(cloud.router, prefix="/cloud", tags=["Cloud"], dependencies=protected)
api_router.include_router(timelapses.router, prefix="/timelapses", tags=["Timelapses"])
api_router.include_router(settings_routes.router, prefix="/settings", tags=["Settings"], dependencies=protected)
