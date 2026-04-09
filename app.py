import os
import shutil
import uuid
from pathlib import Path
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn


def bootstrap_ffmpeg_env() -> None:
    if os.getenv("FFMPEG_BINARY"):
        return

    ffmpeg_on_path = shutil.which("ffmpeg")
    if ffmpeg_on_path:
        os.environ["FFMPEG_BINARY"] = ffmpeg_on_path
        return

    local_appdata = os.getenv("LOCALAPPDATA")
    if not local_appdata:
        return

    winget_root = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
    if not winget_root.exists():
        return

    for package_dir in winget_root.glob("Gyan.FFmpeg*"):
        candidate = package_dir / "ffmpeg-8.1-full_build" / "bin" / "ffmpeg.exe"
        os.environ["FFMPEG_BINARY"] = str(candidate)
        return


bootstrap_ffmpeg_env()

app = FastAPI(title="Multimodal Video Intelligence")

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")


def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list) or isinstance(obj, tuple):
        return [convert_to_serializable(v) for v in obj]
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return convert_to_serializable(obj.tolist())
    if hasattr(obj, "__dict__"):
        return convert_to_serializable(vars(obj))
    return obj


def get_process_video():
    from backend.pipeline import process_video
    return process_video


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/analytics")
async def analytics_page():
    return FileResponse("static/analytics.html")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_video_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".mp4", ".avi", ".mov", ".mkv"]:
        raise HTTPException(status_code=400, detail="Unsupported video format")

    os.makedirs("temp", exist_ok=True)
    temp_video_path = f"temp/upload_{uuid.uuid4().hex}{ext}"

    try:
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        process_video = get_process_video()
        results = process_video(temp_video_path)
        clean_results = convert_to_serializable(results)
        return JSONResponse(content=clean_results)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except OSError:
                pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
