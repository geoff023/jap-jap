from abc import ABC, abstractmethod

from app.schemas.speech import SpeechTranscription


class SpeechServiceError(Exception):
    """Raised whenever a SpeechToTextService implementation can't produce a
    usable transcription — a provider failure, an empty/malformed response,
    or a response that fails validation. Callers translate this into a
    502 Bad Gateway, mirroring AIServiceError's role for AIService."""


class SpeechToTextService(ABC):
    """Application code depends on this interface, never on a specific
    speech provider's SDK — see docs/ARCHITECTURE.md's Speech Abstraction
    (SpeechToTextService -> STTProvider)."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> SpeechTranscription:
        """Transcribe spoken Japanese audio into text."""
