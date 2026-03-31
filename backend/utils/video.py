from __future__ import annotations

from pathlib import Path
from typing import Iterator

import cv2


def iterate_sampled_frames(
    video_path: Path,
    sample_seconds: float,
    max_short_side: int,
) -> Iterator[tuple[float, object]]:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(int(fps * sample_seconds), 1)
    frame_index = 0

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % frame_interval == 0:
                yield round(frame_index / fps, 2), _resize_frame(frame, max_short_side)
            frame_index += 1
    finally:
        capture.release()


def _resize_frame(frame, max_short_side: int):
    height, width = frame.shape[:2]
    short_side = min(height, width)
    if short_side <= max_short_side:
        return frame
    scale = max_short_side / short_side
    return cv2.resize(frame, (int(width * scale), int(height * scale)))
