from __future__ import annotations

from pathlib import Path

from backend.config import PipelineConfig
from backend.models import SpeechSegment


def _translate_if_needed(text: str, language: str) -> str | None:
    if language.lower() in {"hi", "mr"}:
        return f"[Translation unavailable offline] {text}"
    return None


def transcribe_audio(audio_path: Path, config: PipelineConfig) -> list[SpeechSegment]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Install dependencies from requirements.txt."
        ) from exc

    model = WhisperModel(
        config.whisper_model_size,
        device=config.whisper_device,
        compute_type=config.whisper_compute_type,
    )

    segments, info = model.transcribe(
        str(audio_path),
        beam_size=3,
        vad_filter=True,
        multilingual=True,
        condition_on_previous_text=True,
    )

    default_language = (info.language or "unknown").lower()
    transcript: list[SpeechSegment] = []

    for segment in segments:
        text = (segment.text or "").strip()
        avg_logprob = getattr(segment, "avg_logprob", None)
        no_speech_prob = getattr(segment, "no_speech_prob", 0.0) or 0.0
        confidence = _logprob_to_confidence(avg_logprob, no_speech_prob)
        segment_language = getattr(segment, "language", None) or default_language
        transcript.append(
            SpeechSegment(
                start=float(segment.start),
                end=float(segment.end),
                text=text if confidence >= 0.35 else "unclear speech",
                confidence=confidence,
                language=segment_language,
                translated_text=_translate_if_needed(text, segment_language),
            )
        )

    return transcript


def _logprob_to_confidence(avg_logprob: float | None, no_speech_prob: float) -> float:
    if avg_logprob is None:
        return max(0.0, min(1.0, 1.0 - no_speech_prob))
    normalized = max(0.0, min(1.0, 1.0 + (avg_logprob / 5.0)))
    return round(max(0.0, min(1.0, normalized * (1.0 - (no_speech_prob * 0.5)))), 3)
