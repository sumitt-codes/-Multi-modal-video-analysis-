from __future__ import annotations

import subprocess
from pathlib import Path


def extract_audio(video_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(audio_path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg is not installed or not available on PATH. Install FFmpeg to enable audio extraction."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"FFmpeg audio extraction failed: {exc.stderr}") from exc

    return audio_path
