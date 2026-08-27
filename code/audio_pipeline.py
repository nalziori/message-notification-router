"""Audio transcription pipeline.

The Anthropic Messages API does not currently accept audio as a direct
content block (only text, image, and document/PDF are supported as of this
writing) -- so transcription is abstracted behind a TranscriptionProvider
interface with a local, offline default (faster-whisper, which bundles its
own audio decoding via PyAV and needs no system ffmpeg install). Swapping in
a hosted ASR API later means implementing TranscriptionProvider.transcribe()
against that API and changing one line in get_provider().
"""

import datetime
from abc import ABC, abstractmethod
from pathlib import Path

import config
from cache import content_hash, is_success, load_cached, run_with_retries, save_cached


class TranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(self, path: Path) -> tuple[str, str]:
        """Return (transcript_text, model_identifier). Raise on failure."""
        raise NotImplementedError


class LocalWhisperProvider(TranscriptionProvider):
    """Offline transcription via faster-whisper (CTranslate2 + PyAV).
    No API key, no per-call cost, no system ffmpeg dependency."""

    def __init__(self):
        self._model = None

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                config.WHISPER_MODEL_SIZE,
                device=config.WHISPER_DEVICE,
                compute_type=config.WHISPER_COMPUTE_TYPE,
            )
        return self._model

    def transcribe(self, path: Path) -> tuple[str, str]:
        model = self._get_model()
        segments, _info = model.transcribe(str(path), beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text, f"faster-whisper:{config.WHISPER_MODEL_SIZE}"


def get_provider() -> TranscriptionProvider:
    return LocalWhisperProvider()


_provider_singleton: TranscriptionProvider | None = None


def _shared_provider() -> TranscriptionProvider:
    global _provider_singleton
    if _provider_singleton is None:
        _provider_singleton = get_provider()
    return _provider_singleton


def process_audio(
    voice_note_id: str,
    file_path: Path,
    linked_message_ids: list[str],
    linked_user_ids: list[str],
    force: bool = False,
) -> dict:
    """Transcribe one voice note with content-hash caching and retries."""
    digest = content_hash(file_path)
    if not force:
        cached = load_cached(config.AUDIO_CACHE_DIR, digest)
        if is_success(cached):
            return {**cached, "voice_note_id": voice_note_id, "from_cache": True}

    provider = _shared_provider()

    def attempt():
        text, model_id = provider.transcribe(file_path)
        return {"status": "success", "text": text, "model": model_id}

    result = run_with_retries(attempt)
    record = {
        "voice_note_id": voice_note_id,
        "file_path": str(file_path),
        "content_hash": digest,
        "linked_message_ids": linked_message_ids,
        "linked_user_ids": linked_user_ids,
        "processed_at": datetime.datetime.now().astimezone().isoformat(),
        "from_cache": False,
        **result,
    }
    save_cached(config.AUDIO_CACHE_DIR, digest, record)
    return record
