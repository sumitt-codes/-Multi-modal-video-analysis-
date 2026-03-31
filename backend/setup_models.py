import os
import sys
import warnings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')

print("Starting model setup...")

try:
    print("Testing FFmpeg...")
    import ffmpeg
    try:
        ffmpeg.probe(os.path.abspath(__file__)) 
    except Exception as e:
        if "ffprobe" in str(e).lower() or "ffmpeg" in str(e).lower() or isinstance(e, FileNotFoundError):
            print("WARNING: FFmpeg might not be installed or on PATH. Please install it.")
except ImportError:
    pass

print("Initializing Faster-Whisper (auto-downloading weights if missing)...")
try:
    from backend.speech.whisper_model import load_whisper_model
    _ = load_whisper_model("base")
    print("[✓] Whisper ready")
except Exception as e:
    print(f"[X] Whisper failed: {e}")

print("Initializing DeepFace (auto-downloading weights if missing)...")
try:
    from deepface import DeepFace
    import numpy as np
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    _ = DeepFace.analyze(img_path=dummy_img, actions=['emotion'], enforce_detection=False, silent=True)
    print("[✓] DeepFace ready")
except Exception as e:
    print(f"[X] DeepFace failed: {e}")

print("Initializing MediaPipe...")
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        _ = pose.process(dummy_img)
    print("[✓] MediaPipe ready")
except Exception as e:
    print(f"[X] MediaPipe failed: {e}")

print("Setup Complete!")
