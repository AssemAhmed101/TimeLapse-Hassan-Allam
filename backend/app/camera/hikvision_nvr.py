from pathlib import Path

from app.camera.hikvision import HikvisionCamera


class HikvisionNVR(HikvisionCamera):
    def __init__(
        self,
        *,
        host: str,
        username: str,
        password: str,
        output_dir: Path,
        channel: int = 1,
        timeout_seconds: float = 10.0,
        verify_ssl: bool = False,
        scheme: str = "http",
        port: int | None = None,
        ptz_preset_id: int | None = None,
        ptz_settle_seconds: int = 15,
    ):
        super().__init__(
            host=host,
            username=username,
            password=password,
            output_dir=output_dir,
            channel=channel,
            timeout_seconds=timeout_seconds,
            verify_ssl=verify_ssl,
            scheme=scheme,
            port=port,
            ptz_preset_id=ptz_preset_id,
            ptz_settle_seconds=ptz_settle_seconds,
        )
