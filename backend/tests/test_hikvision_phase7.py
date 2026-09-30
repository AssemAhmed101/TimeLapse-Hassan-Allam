from pathlib import Path
from io import BytesIO
import tempfile

import httpx
from PIL import Image

import app.camera.hikvision as hikvision_module
from app.camera.hikvision import HikvisionCamera


class FakeResponse:
    def __init__(
        self,
        status_code=200,
        content=b"image-bytes",
        headers=None,
    ):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"content-type": "image/jpeg"}


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.requested_urls = []
        self.put_urls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get(self, url):
        self.requested_urls.append(url)
        return self.response

    def put(self, url):
        self.put_urls.append(url)
        return FakeResponse(status_code=200)


def jpeg_bytes():
    output = BytesIO()
    Image.new("RGB", (32, 32), color="blue").save(output, format="JPEG")
    return output.getvalue()


def test_hikvision_base_urls():
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="secret",
            output_dir=Path(td),
            channel=1,
            port=80,
        )

        assert camera.base_url == "http://192.168.1.50:80"
        assert camera.device_info_url.endswith("/ISAPI/System/deviceInfo")
        assert camera.snapshot_url.endswith(
            "/ISAPI/Streaming/channels/101/picture"
        )


def test_hikvision_connection_success(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="secret",
            output_dir=Path(td),
            min_snapshot_bytes=1,
        )

        fake = FakeClient(FakeResponse(status_code=200))
        monkeypatch.setattr(camera, "_client", lambda: fake)

        result = camera.test_connection()

        assert result["connected"] is True
        assert result["status_code"] == 200


def test_hikvision_snapshot_success(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="secret",
            output_dir=Path(td),
            min_snapshot_bytes=1,
        )

        fake = FakeClient(
            FakeResponse(
                status_code=200,
                content=jpeg_bytes(),
                headers={"content-type": "image/jpeg"},
            )
        )
        monkeypatch.setattr(camera, "_client", lambda: fake)

        path = camera.capture_snapshot()

        assert path.exists()
        assert path.read_bytes() == jpeg_bytes()


def test_ptz_preset_move_happens_before_snapshot(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="secret",
            output_dir=Path(td),
            ptz_preset_id=2,
            ptz_settle_seconds=15,
            min_snapshot_bytes=1,
        )
        fake = FakeClient(FakeResponse(content=jpeg_bytes()))
        sleeps = []
        monkeypatch.setattr(camera, "_client", lambda: fake)
        monkeypatch.setattr(hikvision_module.time, "sleep", sleeps.append)

        path = camera.capture_snapshot()

        assert fake.put_urls == [camera.ptz_preset_url]
        assert fake.requested_urls == [camera.snapshot_url]
        assert sleeps == [15]
        assert "preset-2" in path.name


def test_invalid_snapshot_is_rejected(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="secret",
            output_dir=Path(td),
            min_snapshot_bytes=1,
        )
        fake = FakeClient(FakeResponse(content=b"not-a-real-image"))
        monkeypatch.setattr(camera, "_client", lambda: fake)

        try:
            camera.capture_snapshot()
            assert False, "invalid image should fail"
        except Exception as exc:
            assert "invalid image data" in str(exc)


def test_hikvision_auth_failure(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        camera = HikvisionCamera(
            host="192.168.1.50",
            username="admin",
            password="wrong",
            output_dir=Path(td),
        )

        fake = FakeClient(FakeResponse(status_code=401))
        monkeypatch.setattr(camera, "_client", lambda: fake)

        result = camera.test_connection()

        assert result["connected"] is False
        assert result["status_code"] == 401
