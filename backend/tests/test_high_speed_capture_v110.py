from pathlib import Path
import tempfile

from app.camera.simulator import SimulatorCamera
from app.schemas.high_speed_capture import HighSpeedCaptureStart
from app.services.high_speed_capture_service import HighSpeedCaptureService


def test_high_speed_schema_accepts_one_second_15_minute_test():
    data = HighSpeedCaptureStart(camera_id=1, interval_seconds=1.0, duration_seconds=900)
    assert data.interval_seconds == 1.0
    assert data.duration_seconds == 900


def test_high_speed_status_is_idle_before_start():
    service = HighSpeedCaptureService()
    status = service.status(99)
    assert status["running"] is False
    assert status["state"] == "idle"
    assert status["captured_snapshots"] == 0


def test_simulator_subsecond_filenames_are_unique():
    with tempfile.TemporaryDirectory() as td:
        camera = SimulatorCamera(Path(td))
        first = camera.capture_snapshot()
        second = camera.capture_snapshot()
        assert first != second
        assert first.exists()
        assert second.exists()


def test_high_speed_routes_are_registered():
    from app.main import app
    # OpenAPI is the stable public view across FastAPI router implementations.
    paths = set(app.openapi()["paths"])
    assert "/api/v1/high-speed-capture/start" in paths
    assert "/api/v1/high-speed-capture/{camera_id}/status" in paths
    assert "/api/v1/high-speed-capture/{camera_id}/stop" in paths
