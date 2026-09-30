import app.services.scheduler_service as scheduler_module
from app.services.scheduler_service import SchedulerService


def test_scheduler_can_register_dispatcher():
    service = SchedulerService()

    service.start()

    try:
        status = service.status()

        assert status["running"] is True
        assert status["dispatcher_registered"] is True
        assert status["dispatcher_job_id"] == "snapshot_dispatcher"
        assert status["engine"] in {
            "apscheduler",
            "threading_fallback",
        }

    finally:
        service.shutdown()


def test_manual_scheduler_cycle_returns_structure(monkeypatch):
    class FakeSession:
        def close(self):
            pass

    monkeypatch.setattr(
        scheduler_module,
        "SessionLocal",
        lambda: FakeSession(),
    )

    monkeypatch.setattr(
        scheduler_module.camera_repository,
        "list",
        lambda db: [],
    )

    service = SchedulerService()
    result = service.run_snapshot_cycle()

    assert result == {
        "camera_count": 0,
        "results": [],
    }
