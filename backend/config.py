from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass(slots=True)
class PipelineConfig:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    uploads_dir: Path = field(init=False)
    outputs_dir: Path = field(init=False)
    temp_dir: Path = field(init=False)
    whisper_model_size: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    frame_sample_seconds: float = 1.0
    pose_sample_seconds: float = 0.5
    max_short_side: int = 720
    emotion_backend: str = "fer"
    supported_video_extensions: Sequence[str] = ("mp4", "avi", "mov", "mkv")

    def __post_init__(self) -> None:
        self.uploads_dir = self.project_root / "data" / "uploads"
        self.outputs_dir = self.project_root / "data" / "outputs"
        self.temp_dir = self.project_root / "temp"

    def ensure_directories(self) -> None:
        for directory in (self.uploads_dir, self.outputs_dir, self.temp_dir):
            directory.mkdir(parents=True, exist_ok=True)


DEFAULT_CONFIG = PipelineConfig()
