from mcp_tts_copilot_summary.config import RuntimeConfig
from mcp_tts_copilot_summary.tools import should_attempt_speech


def test_threshold_met_by_paragraphs() -> None:
    cfg = RuntimeConfig(min_paragraphs=4, min_new_code_lines=100, enabled=True)
    should_speak, _ = should_attempt_speech(cfg, paragraph_count=5, new_code_lines=0)
    assert should_speak is True


def test_threshold_met_by_new_code_lines() -> None:
    cfg = RuntimeConfig(min_paragraphs=4, min_new_code_lines=100, enabled=True)
    should_speak, _ = should_attempt_speech(cfg, paragraph_count=0, new_code_lines=101)
    assert should_speak is True


def test_threshold_not_met_for_equal_values() -> None:
    cfg = RuntimeConfig(min_paragraphs=4, min_new_code_lines=100, enabled=True)
    should_speak, reason = should_attempt_speech(cfg, paragraph_count=4, new_code_lines=100)
    assert should_speak is False
    assert "Threshold not met" in reason


def test_threshold_blocked_when_disabled() -> None:
    cfg = RuntimeConfig(enabled=False)
    should_speak, reason = should_attempt_speech(cfg, paragraph_count=99, new_code_lines=999)
    assert should_speak is False
    assert "disabled" in reason.lower()
