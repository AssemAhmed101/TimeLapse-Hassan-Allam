from abc import ABC, abstractmethod
from pathlib import Path


class CloudStorageError(RuntimeError):
    pass


class CloudStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, local_path: Path, object_key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def exists(self, object_key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_url(self, object_key: str) -> str:
        raise NotImplementedError
