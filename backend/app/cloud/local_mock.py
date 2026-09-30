from pathlib import Path
import shutil

from app.cloud.base import CloudStorageProvider


class LocalMockCloudProvider(CloudStorageProvider):
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

    def upload_file(self, local_path: Path, object_key: str) -> str:
        target = self.root_path / object_key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, target)
        return str(target)

    def exists(self, object_key: str) -> bool:
        return (self.root_path / object_key).exists()

    def get_url(self, object_key: str) -> str:
        return f"mock://{object_key}"
