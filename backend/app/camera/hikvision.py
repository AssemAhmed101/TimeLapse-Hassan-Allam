from datetime import datetime
from io import BytesIO
from pathlib import Path
import time

import httpx
from PIL import Image, UnidentifiedImageError

from app.camera.base import CameraConnectionError, CameraProvider
from app.core.config import settings


class HikvisionCamera(CameraProvider):
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
        min_snapshot_bytes: int | None = None,
    ):
        self.host = host.strip()
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.channel = channel
        self.timeout_seconds = timeout_seconds
        self.verify_ssl = verify_ssl
        self.scheme = scheme
        self.port = port
        self.ptz_preset_id = ptz_preset_id
        self.ptz_settle_seconds = ptz_settle_seconds
        self.min_snapshot_bytes = (
            settings.MIN_SNAPSHOT_BYTES
            if min_snapshot_bytes is None
            else min_snapshot_bytes
        )

    @property
    def base_url(self) -> str:
        port_part = f":{self.port}" if self.port else ""
        return f"{self.scheme}://{self.host}{port_part}"

    @property
    def snapshot_url(self) -> str:
        return (
            f"{self.base_url}"
            f"/ISAPI/Streaming/channels/{self.channel}01/picture"
        )

    @property
    def device_info_url(self) -> str:
        return f"{self.base_url}/ISAPI/System/deviceInfo"

    @property
    def ptz_preset_url(self) -> str | None:
        if self.ptz_preset_id is None:
            return None
        return (
            f"{self.base_url}/ISAPI/PTZCtrl/channels/{self.channel}"
            f"/presets/{self.ptz_preset_id}/goto"
        )

    def _client(self) -> httpx.Client:
        return httpx.Client(
            auth=httpx.DigestAuth(self.username, self.password),
            timeout=self.timeout_seconds,
            verify=self.verify_ssl,
            follow_redirects=True,
        )

    def test_connection(self) -> dict:
        try:
            with self._client() as client:
                response = client.get(self.device_info_url)

            if response.status_code == 200:
                return {
                    "connected": True,
                    "provider": "hikvision",
                    "status_code": 200,
                    "message": "Hikvision device responded successfully",
                }

            if response.status_code in {401, 403}:
                return {
                    "connected": False,
                    "provider": "hikvision",
                    "status_code": response.status_code,
                    "message": "Authentication failed",
                }

            return {
                "connected": False,
                "provider": "hikvision",
                "status_code": response.status_code,
                "message": "Hikvision device returned an unexpected response",
            }

        except httpx.TimeoutException as exc:
            raise CameraConnectionError("Hikvision connection timed out") from exc

        except httpx.RequestError as exc:
            raise CameraConnectionError(
                f"Could not connect to Hikvision device: {exc}"
            ) from exc

    def capture_snapshot(self) -> Path:
        try:
            with self._client() as client:
                if self.ptz_preset_url:
                    preset_response = client.put(self.ptz_preset_url)
                    if preset_response.status_code not in {200, 201, 204}:
                        raise CameraConnectionError(
                            "Hikvision PTZ preset move failed with HTTP "
                            f"{preset_response.status_code}"
                        )
                    if self.ptz_settle_seconds > 0:
                        time.sleep(self.ptz_settle_seconds)
                response = client.get(self.snapshot_url)

            if response.status_code in {401, 403}:
                raise CameraConnectionError(
                    "Hikvision authentication failed"
                )

            if response.status_code != 200:
                raise CameraConnectionError(
                    f"Hikvision snapshot failed with HTTP {response.status_code}"
                )

            content_type = response.headers.get("content-type", "").lower()
            if "image" not in content_type:
                raise CameraConnectionError(
                    "Hikvision snapshot endpoint did not return an image"
                )

            if len(response.content) < self.min_snapshot_bytes:
                raise CameraConnectionError(
                    "Hikvision snapshot is smaller than the configured minimum"
                )

            try:
                with Image.open(BytesIO(response.content)) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError) as exc:
                raise CameraConnectionError(
                    "Hikvision snapshot contains invalid image data"
                ) from exc

            now = datetime.now()
            dated_dir = self.output_dir / now.strftime("%Y/%m/%d")
            dated_dir.mkdir(parents=True, exist_ok=True)

            preset = self.ptz_preset_id or 0
            path = dated_dir / f"{now:%Y-%m-%d_%H-%M-%S_%f}_preset-{preset}.jpg"
            path.write_bytes(response.content)

            return path

        except httpx.TimeoutException as exc:
            raise CameraConnectionError(
                "Hikvision snapshot request timed out"
            ) from exc

        except httpx.RequestError as exc:
            raise CameraConnectionError(
                f"Could not request Hikvision snapshot: {exc}"
            ) from exc
