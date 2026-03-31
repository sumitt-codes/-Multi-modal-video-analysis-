# Multimodal Video Intelligence System

Offline multimodal video analysis for speech, facial emotion, posture, and gesture understanding. The system runs locally, writes structured outputs to disk, and exposes a Streamlit dashboard for upload, processing, and review.

## Features

- Video upload for `mp4`, `avi`, `mov`, and `mkv`
- Audio extraction with FFmpeg
- Multilingual speech recognition with `faster-whisper`
- Facial emotion detection with `FER`
- Body posture and gesture heuristics with `MediaPipe`
- Unified timestamped multimodal timeline
- Streamlit dashboard with video playback, timeline table, key moments, summary text, and a dark or light theme toggle
- Local JSON artifact output at `data/outputs/<video_name>/final_output.json`

## Folder Structure

```text
.
|-- app.py
|-- backend
|   |-- __init__.py
|   |-- config.py
|   |-- models.py
|   |-- pipeline.py
|   |-- audio
|   |   |-- __init__.py
|   |   `-- extractor.py
|   |-- fusion
|   |   |-- __init__.py
|   |   `-- timeline.py
|   |-- speech
|   |   |-- __init__.py
|   |   `-- transcriber.py
|   |-- utils
|   |   |-- __init__.py
|   |   |-- io.py
|   |   `-- video.py
|   `-- vision
|       |-- __init__.py
|       |-- body_language.py
|       `-- emotion.py
|-- data
|   |-- outputs
|   `-- uploads
|-- requirements.txt
`-- README.md
```

## Setup

### 1. Use a supported Python version

Use Python `3.10` or `3.11` for best compatibility with `tensorflow-cpu`, `mediapipe`, and the rest of the local vision stack.

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install FFmpeg

FFmpeg must be available on your system `PATH`.

- Windows: install from the official FFmpeg builds and add the `bin` folder to `PATH`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

### 5. Run the dashboard

```powershell
streamlit run app.py
```

On first run, model weights are downloaded automatically by the libraries:

- Whisper model files for `faster-whisper`
- FER and TensorFlow emotion-model dependencies
- MediaPipe pose models

## Usage

1. Open the Streamlit app.
2. Upload a supported video file.
3. Choose the theme, Whisper model, and frame sampling intervals.
4. Click **Start Processing**.
5. Review the video, transcript, multimodal timeline, key moments, and summary.

## Pipeline Output

The backend exposes:

```python
from backend.pipeline import process_video

output_json = process_video("path/to/video.mp4")
print(output_json)
```

The generated JSON includes:

```json
{
  "video_path": "data/uploads/example.mp4",
  "audio_path": "temp/example.wav",
  "transcript": [],
  "emotions": [],
  "behaviors": [],
  "timeline": [],
  "summary": {
    "detected_languages": [],
    "overall_sentiment_hint": "neutral",
    "key_moments": [],
    "summary_text": "..."
  }
}
```

## Notes For Low-Resource Laptops

- Default Whisper model is `small` on CPU with `int8` compute
- Increase frame sample intervals to reduce vision workload
- Use shorter videos for faster results
- If transcription confidence is low, timeline entries are labeled `unclear speech`

## Limitations

- Hindi and Marathi translation is represented as a placeholder for fully offline mode rather than a full local translation model
- Gesture inference uses lightweight heuristics on pose landmarks rather than a dedicated action-recognition model
- FER performance can vary for profile views or poor lighting

## Sample Run

```powershell
python -c "from backend.pipeline import process_video; print(process_video('sample.mp4'))"
```
