from pathlib import Path
import os
import tempfile
import time

from app.services.storage_service import StorageService


def test_storage_structure_and_stats():
    with tempfile.TemporaryDirectory() as td:
        service = StorageService(Path(td))
        service.ensure_structure()

        assert service.snapshots_path.exists()
        assert service.timelapses_path.exists()

        camera_dir = service.camera_snapshot_dir(3)
        file_path = camera_dir / "test.jpg"
        file_path.write_bytes(b"1234567890")

        status = service.status()

        assert status["snapshots"]["file_count"] == 1
        assert status["snapshots"]["total_bytes"] == 10
        assert status["timelapses"]["file_count"] == 0


def test_cleanup_dry_run_does_not_delete():
    with tempfile.TemporaryDirectory() as td:
        service = StorageService(Path(td))
        old_file = service.camera_snapshot_dir(1) / "old.jpg"
        old_file.write_bytes(b"old")

        old_timestamp = time.time() - (40 * 24 * 60 * 60)
        os.utime(old_file, (old_timestamp, old_timestamp))

        result = service.cleanup(
            dry_run=True,
            snapshot_retention_days=30,
            timelapse_retention_days=365,
        )

        assert result["matched_files"] == 1
        assert result["deleted_files"] == 0
        assert old_file.exists()


def test_cleanup_deletes_old_files():
    with tempfile.TemporaryDirectory() as td:
        service = StorageService(Path(td))
        old_file = service.camera_snapshot_dir(1) / "old.jpg"
        new_file = service.camera_snapshot_dir(1) / "new.jpg"

        old_file.write_bytes(b"old-data")
        new_file.write_bytes(b"new-data")

        old_timestamp = time.time() - (40 * 24 * 60 * 60)
        os.utime(old_file, (old_timestamp, old_timestamp))

        result = service.cleanup(
            dry_run=False,
            snapshot_retention_days=30,
            timelapse_retention_days=365,
        )

        assert result["matched_files"] == 1
        assert result["deleted_files"] == 1
        assert not old_file.exists()
        assert new_file.exists()
        assert result["freed_bytes"] == len(b"old-data")


def test_open_ended_retention_never_matches_files():
    with tempfile.TemporaryDirectory() as td:
        service = StorageService(Path(td))
        old_file = service.camera_snapshot_dir(1) / "old.jpg"
        old_file.write_bytes(b"original")
        old_timestamp = time.time() - (4000 * 24 * 60 * 60)
        os.utime(old_file, (old_timestamp, old_timestamp))

        result = service.cleanup(
            dry_run=False,
            snapshot_retention_days=0,
            timelapse_retention_days=0,
        )

        assert result["matched_files"] == 0
        assert result["deleted_files"] == 0
        assert old_file.exists()


def test_two_camera_six_hour_storage_forecast():
    forecast = StorageService.forecast()

    assert forecast["camera_count"] == 2
    assert forecast["captures_per_camera_per_day"] == 4
    assert forecast["total_images_per_day"] == 8
    assert forecast["annual_images"] == 2920
    assert forecast["estimated_annual_gb"] == 57.031
    assert forecast["estimated_capacity_years"] == 143.64


def test_storage_warning_boundaries():
    assert StorageService.warning_level(69.99) == "normal"
    assert StorageService.warning_level(70) == "warning"
    assert StorageService.warning_level(85) == "high"
    assert StorageService.warning_level(95) == "critical"
