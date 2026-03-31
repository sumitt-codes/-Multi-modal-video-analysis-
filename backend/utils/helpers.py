import os
import json
import uuid


def generate_temp_path(extension=".wav"):
    os.makedirs("temp", exist_ok=True)
    return os.path.join("temp", f"temp_{uuid.uuid4().hex}{extension}")


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def cleanup_file(path):
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
