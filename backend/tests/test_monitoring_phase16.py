from pathlib import Path

from app.services.monitoring_service import MonitoringService


def test_monitoring_status_ok():
    status, warnings = MonitoringService.evaluate_status(
        database_ok=True,
        scheduler_running=True,
        storage_warning=False,
        cloud_configured=True,
    )

    assert status == "ok"
    assert warnings == []


def test_monitoring_status_degraded():
    status, warnings = MonitoringService.evaluate_status(
        database_ok=True,
        scheduler_running=False,
        storage_warning=True,
        cloud_configured=True,
    )

    assert status == "degraded"
    assert "scheduler_not_running" in warnings
    assert "storage_low_space" in warnings


def test_monitoring_status_critical():
    status, warnings = MonitoringService.evaluate_status(
        database_ok=False,
        scheduler_running=True,
        storage_warning=False,
        cloud_configured=True,
    )

    assert status == "critical"
    assert "database_unavailable" in warnings


def test_read_logs_returns_latest_lines(tmp_path, monkeypatch):
    from app.core import config as config_module

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "timelapse.log"
    log_file.write_text(
        "\n".join([f"line {index}" for index in range(10)]),
        encoding="utf-8",
    )

    monkeypatch.setattr(config_module.settings, "LOG_PATH", str(log_dir))

    service = MonitoringService()
    result = service.read_logs(limit=3)

    assert result["count"] == 3
    assert result["lines"] == ["line 7", "line 8", "line 9"]
