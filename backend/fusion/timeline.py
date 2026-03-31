from __future__ import annotations

from collections import Counter

from backend.models import BehaviorSegment, EmotionSegment, ProcessingSummary, SpeechSegment, TimelineEntry


def build_timeline(
    transcript: list[SpeechSegment],
    emotions: list[EmotionSegment],
    behaviors: list[BehaviorSegment],
) -> tuple[list[TimelineEntry], ProcessingSummary]:
    timestamps = sorted(
        {
            *[round(item.start, 2) for item in transcript],
            *[round(item.timestamp, 2) for item in emotions],
            *[round(item.timestamp, 2) for item in behaviors],
        }
    )

    timeline: list[TimelineEntry] = []
    for timestamp in timestamps:
        speech = _closest_speech(timestamp, transcript)
        emotion = _closest_emotion(timestamp, emotions)
        behavior = _closest_behavior(timestamp, behaviors)
        insight = _compose_insight(speech, emotion, behavior)
        timeline.append(
            TimelineEntry(
                timestamp=timestamp,
                speech=speech.text if speech else "",
                speech_confidence=speech.confidence if speech else 0.0,
                emotion=emotion.emotion if emotion else "unknown",
                emotion_confidence=emotion.confidence if emotion else 0.0,
                behavior=_behavior_text(behavior),
                behavior_confidence=behavior.confidence if behavior else 0.0,
                final_insight=insight,
            )
        )

    summary = _build_summary(timeline, transcript)
    return timeline, summary


def _closest_speech(timestamp: float, transcript: list[SpeechSegment]) -> SpeechSegment | None:
    for segment in transcript:
        if segment.start <= timestamp <= segment.end:
            return segment
    if not transcript:
        return None
    return min(transcript, key=lambda item: abs(item.start - timestamp))


def _closest_emotion(timestamp: float, emotions: list[EmotionSegment]) -> EmotionSegment | None:
    if not emotions:
        return None
    return min(emotions, key=lambda item: abs(item.timestamp - timestamp))


def _closest_behavior(timestamp: float, behaviors: list[BehaviorSegment]) -> BehaviorSegment | None:
    if not behaviors:
        return None
    return min(behaviors, key=lambda item: abs(item.timestamp - timestamp))


def _behavior_text(behavior: BehaviorSegment | None) -> str:
    if behavior is None:
        return "unknown"
    gestures = ", ".join(behavior.gestures) if behavior.gestures else "no_distinct_gesture"
    return f"{behavior.posture}; {behavior.head_movement}; {gestures}"


def _compose_insight(
    speech: SpeechSegment | None,
    emotion: EmotionSegment | None,
    behavior: BehaviorSegment | None,
) -> str:
    parts: list[str] = []
    if speech:
        if speech.confidence < 0.35:
            parts.append("Speech is unclear")
        elif speech.text:
            parts.append(f"Speaker discusses: {speech.text}")
    if emotion:
        parts.append(f"emotion appears {emotion.emotion}")
    if behavior:
        if behavior.posture == "slouched":
            parts.append("body posture suggests reduced energy")
        elif "raised_hands" in behavior.gestures:
            parts.append("gestures suggest emphasis")
        elif behavior.head_movement in {"looking_left", "looking_right"}:
            parts.append("head movement suggests shifting attention")
    return ". ".join(parts) if parts else "No strong multimodal signal detected."


def _build_summary(timeline: list[TimelineEntry], transcript: list[SpeechSegment]) -> ProcessingSummary:
    emotions = [item.emotion for item in timeline if item.emotion not in {"unknown", "no_face_detected"}]
    languages = sorted({item.language for item in transcript if item.language})

    dominant_emotion = Counter(emotions).most_common(1)
    sentiment_hint = dominant_emotion[0][0] if dominant_emotion else "neutral"

    key_moments = [
        {
            "timestamp": item.timestamp,
            "insight": item.final_insight,
        }
        for item in timeline
        if item.speech_confidence < 0.4
        or item.emotion in {"angry", "sad", "fear", "surprise"}
        or "raised_hands" in item.behavior
    ][:8]

    if timeline:
        opening = timeline[0]
        summary_text = (
            f"The speaker showed mostly {sentiment_hint} expressions overall. "
            f"Early in the video, behavior looked {opening.behavior}. "
            f"{'Multiple low-confidence speech segments were detected. ' if any(t.speech_confidence < 0.35 for t in timeline) else ''}"
            f"{'Gestural emphasis appeared in several moments. ' if any('raised_hands' in t.behavior for t in timeline) else ''}"
            f"Detected languages: {', '.join(languages) if languages else 'unknown'}."
        )
    else:
        summary_text = "No analyzable multimodal events were detected."

    return ProcessingSummary(
        detected_languages=languages,
        overall_sentiment_hint=sentiment_hint,
        key_moments=key_moments,
        summary_text=summary_text,
    )
