from __future__ import annotations

from typing import Any, Callable


class SapiTtsAdapter:
    SPEAK_FLAG_ASYNC = 1

    def __init__(self, dispatcher: Callable[[str], Any] | None = None) -> None:
        self._dispatcher = dispatcher

    def _dispatch_voice(self) -> Any:
        if self._dispatcher is not None:
            return self._dispatcher("SAPI.SpVoice")

        try:
            import win32com.client  # type: ignore[import-not-found]
        except Exception as exc:
            raise RuntimeError("win32com is unavailable") from exc

        return win32com.client.Dispatch("SAPI.SpVoice")

    def _voice_name(self, voice: Any) -> str:
        try:
            return str(voice.GetDescription())
        except Exception:
            return ""

    def _select_voice(self, voices: list[Any], preferred_voice: str = "zira") -> tuple[Any | None, str | None]:
        if not voices:
            return None, None

        preferred_lower = preferred_voice.lower()
        for voice in voices:
            name = self._voice_name(voice)
            if preferred_lower in name.lower():
                return voice, name

        first_voice = voices[0]
        return first_voice, self._voice_name(first_voice)

    def list_voice_names(self) -> list[str]:
        try:
            speaker = self._dispatch_voice()
            return [self._voice_name(voice) for voice in list(speaker.GetVoices())]
        except Exception:
            return []

    def speak(
        self,
        text: str,
        *,
        rate: int = 0,
        volume: int = 100,
        preferred_voice: str = "zira",
        async_mode: bool = True,
    ) -> dict[str, Any]:
        if not text.strip():
            return {
                "status": "skipped",
                "spoken": False,
                "warning": "Speech skipped because text is empty.",
                "voice_used": None,
            }

        try:
            speaker = self._dispatch_voice()
        except Exception as exc:
            return {
                "status": "skipped",
                "spoken": False,
                "warning": f"Speech skipped: unable to initialize SAPI ({exc}).",
                "voice_used": None,
            }

        try:
            voices = list(speaker.GetVoices())
            chosen_voice, chosen_voice_name = self._select_voice(voices, preferred_voice=preferred_voice)
            if chosen_voice is None:
                return {
                    "status": "skipped",
                    "spoken": False,
                    "warning": "Speech skipped: no SAPI voices available.",
                    "voice_used": None,
                }

            speaker.Rate = max(-10, min(10, int(rate)))
            speaker.Volume = max(0, min(100, int(volume)))
            speaker.Voice = chosen_voice
            speak_flags = self.SPEAK_FLAG_ASYNC if async_mode else 0
            speaker.Speak(text, speak_flags)
            return {
                "status": "spoken",
                "spoken": True,
                "warning": None,
                "voice_used": chosen_voice_name,
                "async_mode": async_mode,
            }
        except Exception as exc:
            return {
                "status": "skipped",
                "spoken": False,
                "warning": f"Speech skipped: SAPI invocation failed ({exc}).",
                "voice_used": None,
            }
