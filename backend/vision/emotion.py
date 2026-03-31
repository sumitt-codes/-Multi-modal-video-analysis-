import cv2
from deepface import DeepFace
import os

def detect_emotions(video_path: str, fps_extraction=1.0):
    print("Running emotion detection (DeepFace)...")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file missing: {video_path}")
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video for emotion detection.")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30.0
        
    frame_interval = int(round(fps / fps_extraction))
    
    results = []
    frame_count = 0
    timestamps_processed = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            
            try:
                analysis = DeepFace.analyze(
                    img_path=frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                
                if isinstance(analysis, list):
                    analysis = analysis[0]
                    
                dominant_emotion = analysis.get('dominant_emotion', 'neutral')
                emotions_dict = analysis.get('emotion', {})
                confidence = emotions_dict.get(dominant_emotion, 0) / 100.0
                
                ts_rounded = round(timestamp, 1)
                if ts_rounded not in timestamps_processed:
                    results.append({
                        "timestamp": ts_rounded,
                        "emotion": dominant_emotion,
                        "confidence": round(confidence, 3)
                    })
                    timestamps_processed.add(ts_rounded)
                    
            except Exception:
                pass
                
        frame_count += 1
        
    cap.release()
    return results
