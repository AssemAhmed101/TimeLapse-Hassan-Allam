from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_settings():
    return {
        "snapshot_interval_seconds": 21600,
        "daily_timelapse_enabled": True
    }
