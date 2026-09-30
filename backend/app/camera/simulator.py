from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from app.camera.base import CameraProvider


class SimulatorCamera(CameraProvider):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def capture_snapshot(self) -> Path:
        now = datetime.now()

        dated_dir = self.output_dir / now.strftime("%Y-%m-%d")
        dated_dir.mkdir(parents=True, exist_ok=True)

        path = dated_dir / f"{now:%Y-%m-%d_%H-%M-%S_%f}.jpg"

        image = Image.new("RGB", (1280, 720), "white")
        draw = ImageDraw.Draw(image)
        draw.text(
            (40, 40),
            f"Simulator Camera\n{now.isoformat()}",
            fill="black",
        )
        image.save(path)

        return path

    def test_connection(self) -> dict:
        return {
            "connected": True,
            "provider": "simulator",
            "message": "Simulator camera is available",
        }
