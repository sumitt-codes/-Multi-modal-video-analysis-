from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


def save_uploaded_file(source_path: Path, uploads_dir: Path) -> Path:
    uploads_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = uploads_dir / f"{timestamp}_{source_path.name}"
    shutil.copy2(source_path, destination)
    return destination


def save_upload_bytes(filename: str, payload: bytes, uploads_dir: Path) -> Path:
    uploads_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = uploads_dir / f"{timestamp}_{Path(filename).name}"
    destination.write_bytes(payload)
    return destination


def dump_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
