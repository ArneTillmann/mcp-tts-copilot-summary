from mcp_tts_copilot_summary.config import RuntimeConfig
from mcp_tts_copilot_summary.tools import speak_existing_summary, speak_text


class FakeAdapter:
    def __init__(self) -> None:
        self.calls = []

    def speak(
        self,
        text: str,
        *,
        rate: int = 0,
        volume: int = 100,
        preferred_voice: str = "zira",
        async_mode: bool = True,
    ):
        self.calls.append(
            {
                "text": text,
                "rate": rate,
                "volume": volume,
                "preferred_voice": preferred_voice,
                "async_mode": async_mode,
            }
        )
        return {
            "status": "spoken",
            "spoken": True,
            "warning": None,
            "voice_used": "Microsoft Zira Desktop",
        }


def test_speak_text_contract_success() -> None:
    cfg = RuntimeConfig(min_paragraphs=4, min_new_code_lines=100, enabled=True, rate=1, volume=90)
    adapter = FakeAdapter()

    result = speak_text(
        "Existing summary text.",
        paragraph_count=5,
        new_code_lines=0,
        cfg=cfg,
        adapter=adapter,
    )

    assert result["tool"] == "speak_text"
    assert result["status"] == "spoken"
    assert result["spoken"] is True
    assert result["voice_used"] == "Microsoft Zira Desktop"
    assert len(adapter.calls) == 1
    assert adapter.calls[0]["async_mode"] is True


def test_speak_existing_summary_skips_when_threshold_not_met() -> None:
    cfg = RuntimeConfig(min_paragraphs=4, min_new_code_lines=100, enabled=True)
    adapter = FakeAdapter()

    result = speak_existing_summary(
        "Short response.",
        paragraph_count=2,
        new_code_lines=10,
        cfg=cfg,
        adapter=adapter,
    )

    assert result["tool"] == "speak_existing_summary"
    assert result["status"] == "skipped"
    assert result["spoken"] is False
    assert len(adapter.calls) == 0


def test_speak_text_skips_for_empty_text() -> None:
    cfg = RuntimeConfig(enabled=True)
    adapter = FakeAdapter()

    result = speak_text("   ", paragraph_count=99, cfg=cfg, adapter=adapter)

    assert result["status"] == "skipped"
    assert result["spoken"] is False
    assert "empty" in result["warning"].lower()
    assert len(adapter.calls) == 0
