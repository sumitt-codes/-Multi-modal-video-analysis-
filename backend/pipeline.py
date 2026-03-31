import os
from backend.utils.helpers import generate_temp_path, cleanup_file
from backend.audio.extract_audio import extract_audio
from backend.speech.whisper_model import load_whisper_model, run_speech_recognition
from backend.vision.emotion import detect_emotions
from backend.vision.pose import detect_pose
from backend.fusion.fusion_engine import fuse_results

_whisper_model = None


def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = load_whisper_model("small")
    return _whisper_model


def process_video(video_path: str):
    print(f"--- Starting Pipeline for {video_path} ---")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video not found: {video_path}")

    temp_audio_path = generate_temp_path(".wav")

    try:
        print("[1/5] Extracting audio...")
        extract_audio(video_path, temp_audio_path)

        print("[2/5] Running speech recognition...")
        model = get_whisper()
        speech_results = run_speech_recognition(model, temp_audio_path)

        print("[3/5] Running emotion detection (DeepFace)...")
        emotion_results = detect_emotions(video_path, fps_extraction=1.0)

        print("[4/5] Running pose detection (MediaPipe)...")
        pose_results = detect_pose(video_path, fps_extraction=1.0)

        print("[5/5] Fusing multimodal data...")
        timeline = fuse_results(speech_results, emotion_results, pose_results)

        return {
            "speech": speech_results,
            "emotion": emotion_results,
            "behavior": pose_results,
            "timeline": timeline,
        }

    finally:
        cleanup_file(temp_audio_path)
        print("--- Pipeline Completed ---")
