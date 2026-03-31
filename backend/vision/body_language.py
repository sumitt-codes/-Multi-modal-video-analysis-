from __future__ import annotations

import math
from pathlib import Path

import cv2

from backend.config import PipelineConfig
from backend.models import BehaviorSegment
from backend.utils.video import iterate_sampled_frames


def analyze_body_language(video_path: Path, config: PipelineConfig) -> list[BehaviorSegment]:
    try:
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError("MediaPipe is not installed. Install dependencies from requirements.txt.") from exc

    mp_pose = mp.solutions.pose
    behaviors: list[BehaviorSegment] = []

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for timestamp, frame in iterate_sampled_frames(
            video_path, config.pose_sample_seconds, config.max_short_side
        ):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if not result.pose_landmarks:
                behaviors.append(
                    BehaviorSegment(
                        timestamp=timestamp,
                        head_movement="unknown",
                        posture="pose_not_detected",
                        gestures=[],
                        confidence=0.0,
                    )
                )
                continue

            landmarks = result.pose_landmarks.landmark
            posture = _infer_posture(landmarks)
            head_movement = _infer_head_movement(landmarks)
            gestures = _infer_gestures(landmarks)
            visibility = _mean_visibility(landmarks)
            behaviors.append(
                BehaviorSegment(
                    timestamp=timestamp,
                    head_movement=head_movement,
                    posture=posture,
                    gestures=gestures,
                    confidence=round(visibility, 3),
                )
            )

    return behaviors


def _infer_posture(landmarks) -> str:
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]

    shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_center_y = (left_hip.y + right_hip.y) / 2
    torso_length = abs(hip_center_y - shoulder_center_y)
    shoulder_tilt = abs(left_shoulder.y - right_shoulder.y)

    if shoulder_tilt > 0.08:
        return "leaning"
    if torso_length < 0.18:
        return "slouched"
    return "upright"


def _infer_head_movement(landmarks) -> str:
    nose = landmarks[0]
    left_ear = landmarks[7]
    right_ear = landmarks[8]

    ear_mid_x = (left_ear.x + right_ear.x) / 2
    dx = nose.x - ear_mid_x
    dy = nose.y - ((left_ear.y + right_ear.y) / 2)

    if dx > 0.05:
        return "looking_right"
    if dx < -0.05:
        return "looking_left"
    if dy > 0.04:
        return "head_down"
    if dy < -0.04:
        return "head_up"
    return "steady"


def _infer_gestures(landmarks) -> list[str]:
    gestures: list[str] = []
    left_wrist = landmarks[15]
    right_wrist = landmarks[16]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_elbow = landmarks[13]
    right_elbow = landmarks[14]

    if left_wrist.y < left_shoulder.y or right_wrist.y < right_shoulder.y:
        gestures.append("raised_hands")

    left_arm_angle = _angle(left_shoulder, left_elbow, left_wrist)
    right_arm_angle = _angle(right_shoulder, right_elbow, right_wrist)
    if left_arm_angle < 70 or right_arm_angle < 70:
        gestures.append("expressive_hand_motion")

    wrist_gap = abs(left_wrist.x - right_wrist.x)
    if wrist_gap < 0.08:
        gestures.append("hands_close_together")

    return gestures


def _angle(a, b, c) -> float:
    ab = (a.x - b.x, a.y - b.y)
    cb = (c.x - b.x, c.y - b.y)
    dot = (ab[0] * cb[0]) + (ab[1] * cb[1])
    mag_ab = math.sqrt((ab[0] ** 2) + (ab[1] ** 2))
    mag_cb = math.sqrt((cb[0] ** 2) + (cb[1] ** 2))
    if mag_ab == 0 or mag_cb == 0:
        return 180.0
    cosine = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))
    return math.degrees(math.acos(cosine))


def _mean_visibility(landmarks) -> float:
    visibilities = [landmark.visibility for landmark in landmarks if landmark.visibility is not None]
    if not visibilities:
        return 0.0
    return sum(visibilities) / len(visibilities)
