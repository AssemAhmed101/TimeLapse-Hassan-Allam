from pathlib import Path
import tempfile

from app.cloud.local_mock import LocalMockCloudProvider


def test_local_mock_upload_and_exists():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cloud_root = root / "cloud"
        source = root / "source.txt"

        source.write_text("hello", encoding="utf-8")

        provider = LocalMockCloudProvider(cloud_root)

        url = provider.upload_file(
            source,
            "project/test/source.txt",
        )

        assert provider.exists("project/test/source.txt") is True
        assert url == str(cloud_root / "project/test/source.txt")


def test_local_mock_url():
    with tempfile.TemporaryDirectory() as td:
        provider = LocalMockCloudProvider(Path(td))
        assert provider.get_url("a/b.jpg") == "mock://a/b.jpg"
