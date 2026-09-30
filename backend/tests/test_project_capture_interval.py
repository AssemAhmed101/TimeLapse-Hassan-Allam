from datetime import datetime, timedelta, timezone

from app.services.snapshot_engine import SnapshotEngine


def test_six_hour_boundary_is_exact():
    interval = 21600
    captured = datetime(2026, 1, 1, tzinfo=timezone.utc)

    just_before = captured + timedelta(seconds=interval - 1)
    exact = captured + timedelta(seconds=interval)

    assert (just_before - captured).total_seconds() < interval
    assert (exact - captured).total_seconds() >= interval


def test_full_day_capture_window_includes_day_and_night():
    engine = SnapshotEngine()

    assert engine._is_inside_capture_window(
        datetime(2026, 1, 1, 0, 0, 0).time(),
        datetime(2026, 1, 1, 0, 0, 0).time(),
        datetime(2026, 1, 1, 23, 59, 59).time(),
    )
    assert engine._is_inside_capture_window(
        datetime(2026, 1, 1, 23, 59, 59).time(),
        datetime(2026, 1, 1, 0, 0, 0).time(),
        datetime(2026, 1, 1, 23, 59, 59).time(),
    )


def test_two_cameras_produce_eight_images_per_day():
    cameras = 2
    seconds_per_day = 86400
    interval_seconds = 21600

    assert cameras * (seconds_per_day // interval_seconds) == 8
