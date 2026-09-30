from abc import ABC, abstractmethod
from pathlib import Path


class CameraConnectionError(RuntimeError):
    pass


class CameraProvider(ABC):
    @abstractmethod
    def capture_snapshot(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> dict:
        raise NotImplementedError
