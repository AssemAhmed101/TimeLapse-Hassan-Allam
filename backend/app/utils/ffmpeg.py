from pathlib import Path
import shutil
import subprocess
import tempfile


class FFmpegError(RuntimeError):
    pass


def get_ffmpeg_path() -> str | None:
    return shutil.which("ffmpeg")


def get_ffprobe_path() -> str | None:
    return shutil.which("ffprobe")


def is_ffmpeg_available() -> bool:
    return get_ffmpeg_path() is not None


def build_timelapse(
    image_paths: list[Path],
    output_path: Path,
    fps: int = 25,
    output_width: int | None = None,
    output_height: int | None = None,
) -> Path:
    ffmpeg = get_ffmpeg_path()

    if ffmpeg is None:
        raise FFmpegError(
            "FFmpeg is not installed or not available in PATH."
        )

    if not image_paths:
        raise FFmpegError("No snapshot images were provided.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        concat_file = Path(temp_dir) / "frames.txt"

        with concat_file.open("w", encoding="utf-8") as f:
            for image in image_paths:
                escaped = str(image.resolve()).replace("'", r"'\''")
                f.write(f"file '{escaped}'\n")

        cmd = [
            ffmpeg,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-r", str(fps),
            "-i", str(concat_file),
        ]

        if output_width and output_height:
            cmd += [
                "-vf",
                f"scale={output_width}:{output_height}:force_original_aspect_ratio=decrease,"
                f"pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2",
            ]

        cmd += [
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise FFmpegError(
                result.stderr.strip() or "FFmpeg failed to generate time-lapse."
            )

    return output_path
