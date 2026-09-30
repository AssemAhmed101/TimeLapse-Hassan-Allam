from app.services.scheduler_service import scheduler_service


def start_snapshot_scheduler() -> None:
    scheduler_service.start()


def stop_snapshot_scheduler() -> None:
    scheduler_service.shutdown()
