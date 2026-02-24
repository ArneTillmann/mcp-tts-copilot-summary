import platform

import pytest

from mcp_tts_copilot_summary.tts.sapi import SapiTtsAdapter


class FakeVoice:
    def __init__(self, name: str) -> None:
        self._name = name

    def GetDescription(self) -> str:
        return self._name


class FakeSpeaker:
    def __init__(self, voices: list[FakeVoice]) -> None:
        self._voices = voices
        self.Rate = 0
        self.Volume = 100
        self.Voice = None
        self.spoken = []
        self.flags = []

    def GetVoices(self):
        return self._voices

    def Speak(self, text: str, flags: int = 0) -> None:
        self.spoken.append(text)
        self.flags.append(flags)


def _dispatcher_with_speaker(speaker: FakeSpeaker):
    def _dispatch(name: str):
        assert name == "SAPI.SpVoice"
        return speaker

    return _dispatch


def test_prefers_zira_when_present() -> None:
    speaker = FakeSpeaker([
        FakeVoice("Microsoft David Desktop"),
        FakeVoice("Microsoft Zira Desktop"),
    ])
    adapter = SapiTtsAdapter(dispatcher=_dispatcher_with_speaker(speaker))

    result = adapter.speak("hello", preferred_voice="zira")

    assert result["status"] == "spoken"
    assert result["spoken"] is True
    assert result["voice_used"] == "Microsoft Zira Desktop"
    assert speaker.flags == [SapiTtsAdapter.SPEAK_FLAG_ASYNC]


def test_falls_back_to_first_voice_when_zira_missing() -> None:
    speaker = FakeSpeaker([
        FakeVoice("Microsoft David Desktop"),
        FakeVoice("Microsoft Mark Desktop"),
    ])
    adapter = SapiTtsAdapter(dispatcher=_dispatcher_with_speaker(speaker))

    result = adapter.speak("hello", preferred_voice="zira")

    assert result["status"] == "spoken"
    assert result["voice_used"] == "Microsoft David Desktop"


def test_skips_when_no_voices_are_available() -> None:
    speaker = FakeSpeaker([])
    adapter = SapiTtsAdapter(dispatcher=_dispatcher_with_speaker(speaker))

    result = adapter.speak("hello", preferred_voice="zira")

    assert result["status"] == "skipped"
    assert result["spoken"] is False
    assert "no sapi voices" in result["warning"].lower()


@pytest.mark.optional_windows
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only optional check")
def test_optional_windows_zira_presence() -> None:
    adapter = SapiTtsAdapter()
    voices = adapter.list_voice_names()

    if not voices:
        pytest.skip("No SAPI voices available on this machine")
    if not any("zira" in voice.lower() for voice in voices):
        pytest.skip("Zira unavailable on this machine")

    assert any("zira" in voice.lower() for voice in voices)
