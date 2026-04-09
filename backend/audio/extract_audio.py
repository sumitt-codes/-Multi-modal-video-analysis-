import os
import shutil
import subprocess
from pathlib import Path


def _resolve_ffmpeg_binary() -> str:
    env_binary = os.getenv("FFMPEG_BINARY")
    if env_binary:
        return env_binary

    which_binary = shutil.which("ffmpeg")
    if which_binary:
        return which_binary

    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        winget_root = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
        if winget_root.exists():
            for package_dir in winget_root.glob("Gyan.FFmpeg*"):
                candidate = package_dir / "ffmpeg-8.1-full_build" / "bin" / "ffmpeg.exe"
                return str(candidate)

    raise RuntimeError(
        "FFmpeg executable was not found. Install FFmpeg and add it to PATH, or set the FFMPEG_BINARY environment variable to ffmpeg.exe."
    )


def extract_audio(video_path: str, output_path: str) -> str:
    """Extract audio from a video into mono 16kHz WAV using the FFmpeg executable."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ffmpeg_binary = _resolve_ffmpeg_binary()
    command = [
        ffmpeg_binary,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]

    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            f"FFmpeg executable could not be started at '{ffmpeg_binary}'. Verify FFmpeg is installed correctly and available on PATH."
        ) from e
    except PermissionError as e:
        raise RuntimeError(
            f"FFmpeg was found but Windows denied access to '{ffmpeg_binary}'. Try running from start_server.bat or reinstalling FFmpeg."
        ) from e
    except subprocess.CalledProcessError as e:
        error_output = (e.stderr or e.stdout or str(e)).strip()
        raise RuntimeError(f"FFmpeg audio extraction failed: {error_output}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during audio extraction: {e}") from e

    if not os.path.exists(output_path):
        raise RuntimeError(
            f"FFmpeg finished without creating the audio file at {output_path}. Output: {(completed.stderr or completed.stdout or '').strip()}"
        )

    return output_path
