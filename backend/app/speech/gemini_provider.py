import json

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.schemas.speech import SpeechTranscription
from app.speech.base import SpeechServiceError, SpeechToTextService

DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiSTTProvider(SpeechToTextService):
    """Gemini-backed STTProvider — Gemini 2.0 Flash accepts audio input
    directly, so this reuses the same google-genai SDK as GeminiService
    rather than adding a second AI vendor/SDK just for transcription.
    Configured via its own STT_API_KEY (see Settings), independent of
    GEMINI_API_KEY, so speech features can be enabled/disabled separately
    from the AI tutor/generation features.
    """

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> SpeechTranscription:
        prompt = (
            "Transcribe the spoken Japanese in this audio exactly as spoken, in "
            "standard Japanese script (hiragana/katakana/kanji as appropriate) — "
            "no romaji, no translation, no commentary. "
            "Respond with ONLY a JSON object (no markdown, no extra text) with "
            'exactly this key: "transcript" (the transcription; an empty string '
            "if no speech is audible)."
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
        except Exception as exc:
            raise SpeechServiceError("Speech provider request failed") from exc

        text = response.text
        if not text:
            raise SpeechServiceError("Speech provider returned an empty response")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SpeechServiceError("Speech provider returned a non-JSON response") from exc

        try:
            return SpeechTranscription.model_validate(data)
        except ValidationError as exc:
            raise SpeechServiceError(
                "Speech provider's transcription didn't match the expected format"
            ) from exc
