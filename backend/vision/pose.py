import cv2
import numpy as np
import os

try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    HAS_MEDIAPIPE = True
except Exception as e:
    print(f"Warning: MediaPipe failed to load ({e}). Behavior track will be skipped.")
    HAS_MEDIAPIPE = False

def detect_pose(video_path: str, fps_extraction=1.0):
    print("Running pose/behavior detection...")
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video not found.")
        
    if not HAS_MEDIAPIPE:
        return []
        
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30.0
        
    frame_interval = int(round(fps / fps_extraction))
    
    results = []
    frame_count = 0
    prev_landmarks = None
    
    # Check if Pose module is actually accessible locally
    if HAS_MEDIAPIPE:
        try:
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    if frame_count % frame_interval == 0:
                        timestamp = frame_count / fps
                        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image_rgb.flags.writeable = False
                        pose_results = pose.process(image_rgb)
                        
                        behavior = "stable"
                        if pose_results.pose_landmarks:
                            current_landmarks = np.array([[lmk.x, lmk.y, lmk.z] for lmk in pose_results.pose_landmarks.landmark])
                            
                            if prev_landmarks is not None:
                                movement = np.mean(np.linalg.norm(current_landmarks - prev_landmarks, axis=1))
                                if movement > 0.05:
                                    behavior = "moving"
                                elif movement > 0.01:
                                    behavior = "fidgeting"
                                    
                            prev_landmarks = current_landmarks
                        else:
                            behavior = "unknown"
                            
                        results.append({
                            "timestamp": round(timestamp, 1),
                            "behavior": behavior
                        })
                        
                    frame_count += 1
        except Exception as ex:
            print(f"Pose tracking failed at runtime: {ex}")
            
    cap.release()
    return results
