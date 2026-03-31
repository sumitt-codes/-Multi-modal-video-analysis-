import os
import math
from faster_whisper import WhisperModel


def load_whisper_model(model_size="small", device="cpu", compute_type="int8"):
    print(f"Loading Faster-Whisper '{model_size}' model...")
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def run_speech_recognition(model, audio_path: str):
    """
    Returns list of transcribed segments.
    [{'start': float, 'end': float, 'text': str, 'confidence': float, 'language': str}]
    """
    print("Running speech recognition...")
    if not os.path.exists(audio_path):
        print(f"Audio file [{audio_path}] missing. Skipping speech recognition.")
        return []

    segments, info = model.transcribe(
        audio_path,
        beam_size=3,
        vad_filter=True,
        multilingual=True,
        condition_on_previous_text=True,
        task="transcribe",
    )

    detected_language = getattr(info, "language", None) or "unknown"
    results = []
    for segment in segments:
        original_text = (segment.text or "").strip()
        if not original_text:
            continue

        avg_logprob = getattr(segment, "avg_logprob", None)
        no_speech_prob = float(getattr(segment, "no_speech_prob", 0.0) or 0.0)
        confidence = _segment_confidence(avg_logprob, no_speech_prob)
        text = original_text if confidence >= 0.35 else "unclear speech"

        results.append({
            "start": round(float(segment.start), 2),
            "end": round(float(segment.end), 2),
            "text": text,
            "confidence": round(confidence, 3),
            "language": detected_language,
            "original_text": original_text,
        })

    print(f"Detected speech language: {detected_language}")
    return results


def _segment_confidence(avg_logprob, no_speech_prob: float) -> float:
    if avg_logprob is None:
        return max(0.0, min(1.0, 1.0 - no_speech_prob))

    normalized = 1.0 / (1.0 + math.exp(-avg_logprob))
    confidence = normalized * (1.0 - (no_speech_prob * 0.5))
    return max(0.0, min(1.0, confidence))
