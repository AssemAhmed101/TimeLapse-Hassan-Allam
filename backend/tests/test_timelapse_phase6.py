from pathlib import Path
import tempfile

import pytest
from PIL import Image

import app.utils.ffmpeg as ffmpeg_module
from app.utils.ffmpeg import FFmpegError, build_timelapse


def test_ffmpeg_unavailable(monkeypatch):
    monkeypatch.setattr(ffmpeg_module, "get_ffmpeg_path", lambda: None)

    with pytest.raises(FFmpegError):
        build_timelapse(
            image_paths=[Path("a.jpg")],
            output_path=Path("out.mp4"),
        )


def test_build_timelapse_command(monkeypatch):
    class Result:
        returncode = 0
        stderr = ""

    monkeypatch.setattr(
        ffmpeg_module,
        "get_ffmpeg_path",
        lambda: "ffmpeg",
    )
    monkeypatch.setattr(
        ffmpeg_module.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        a = temp / "a.jpg"
        b = temp / "b.jpg"

        Image.new("RGB", (320, 240), "white").save(a)
        Image.new("RGB", (320, 240), "black").save(b)

        result = build_timelapse(
            image_paths=[a, b],
            output_path=temp / "out.mp4",
            fps=25,
        )

        assert result.name == "out.mp4"
