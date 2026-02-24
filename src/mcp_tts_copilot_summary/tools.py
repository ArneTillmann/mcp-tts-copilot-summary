from __future__ import annotations

from typing import Any

from .config import RuntimeConfig, load_config
from .tts.sapi import SapiTtsAdapter


def should_attempt_speech(
    cfg: RuntimeConfig,
    paragraph_count: int | None = None,
    new_code_lines: int | None = None,
) -> tuple[bool, str]:
    if not cfg.enabled:
        return False, "Speech is disabled by configuration."

    if paragraph_count is None and new_code_lines is None:
        return True, "No metadata provided; proceeding with speech."

    paragraph_value = paragraph_count or 0
    new_code_value = new_code_lines or 0

    if paragraph_value > cfg.min_paragraphs or new_code_value > cfg.min_new_code_lines:
        return True, "Threshold met."

    return (
        False,
        f"Threshold not met: requires paragraphs>{cfg.min_paragraphs} or new_code_lines>{cfg.min_new_code_lines}.",
    )


def _speak_common(
    summary_text: str,
    *,
    paragraph_count: int | None,
    new_code_lines: int | None,
    rate: int | None,
    volume: int | None,
    cfg: RuntimeConfig,
    adapter: SapiTtsAdapter,
    tool_name: str,
) -> dict[str, Any]:
    if not summary_text.strip():
        return {
            "tool": tool_name,
            "status": "skipped",
            "spoken": False,
            "warning": "Speech skipped because summary_text is empty.",
            "voice_used": None,
            "paragraph_count": paragraph_count,
            "new_code_lines": new_code_lines,
        }

    should_speak, reason = should_attempt_speech(
        cfg,
        paragraph_count=paragraph_count,
        new_code_lines=new_code_lines,
    )
    if not should_speak:
        return {
            "tool": tool_name,
            "status": "skipped",
            "spoken": False,
            "warning": reason,
            "voice_used": None,
            "paragraph_count": paragraph_count,
            "new_code_lines": new_code_lines,
        }

    result = adapter.speak(
        summary_text,
        rate=cfg.rate if rate is None else rate,
        volume=cfg.volume if volume is None else volume,
        preferred_voice="zira",
        async_mode=cfg.async_speech,
    )
    return {
        "tool": tool_name,
        **result,
        "decision_reason": reason,
        "paragraph_count": paragraph_count,
        "new_code_lines": new_code_lines,
    }


def speak_text(
    summary_text: str,
    paragraph_count: int | None = None,
    new_code_lines: int | None = None,
    rate: int | None = None,
    volume: int | None = None,
    *,
    cfg: RuntimeConfig | None = None,
    adapter: SapiTtsAdapter | None = None,
) -> dict[str, Any]:
    runtime_cfg = cfg or load_config()
    tts_adapter = adapter or SapiTtsAdapter()
    return _speak_common(
        summary_text,
        paragraph_count=paragraph_count,
        new_code_lines=new_code_lines,
        rate=rate,
        volume=volume,
        cfg=runtime_cfg,
        adapter=tts_adapter,
        tool_name="speak_text",
    )


def speak_existing_summary(
    summary_text: str,
    paragraph_count: int | None = None,
    new_code_lines: int | None = None,
    rate: int | None = None,
    volume: int | None = None,
    *,
    cfg: RuntimeConfig | None = None,
    adapter: SapiTtsAdapter | None = None,
) -> dict[str, Any]:
    runtime_cfg = cfg or load_config()
    tts_adapter = adapter or SapiTtsAdapter()
    return _speak_common(
        summary_text,
        paragraph_count=paragraph_count,
        new_code_lines=new_code_lines,
        rate=rate,
        volume=volume,
        cfg=runtime_cfg,
        adapter=tts_adapter,
        tool_name="speak_existing_summary",
    )


def register_tools(mcp: Any, cfg: RuntimeConfig | None = None, adapter: SapiTtsAdapter | None = None) -> None:
    runtime_cfg = cfg or load_config()
    tts_adapter = adapter or SapiTtsAdapter()

    @mcp.tool(
        name="speak_text",
        description="Speak provided summary text with SAPI Zira preference and fallback voice behavior.",
    )
    def _tool_speak_text(
        summary_text: str,
        paragraph_count: int | None = None,
        new_code_lines: int | None = None,
        rate: int | None = None,
        volume: int | None = None,
    ) -> dict[str, Any]:
        return speak_text(
            summary_text,
            paragraph_count=paragraph_count,
            new_code_lines=new_code_lines,
            rate=rate,
            volume=volume,
            cfg=runtime_cfg,
            adapter=tts_adapter,
        )

    @mcp.tool(
        name="speak_existing_summary",
        description="Speak already-prepared summary text from model output with metadata-aware guard checks.",
    )
    def _tool_speak_existing_summary(
        summary_text: str,
        paragraph_count: int | None = None,
        new_code_lines: int | None = None,
        rate: int | None = None,
        volume: int | None = None,
    ) -> dict[str, Any]:
        return speak_existing_summary(
            summary_text,
            paragraph_count=paragraph_count,
            new_code_lines=new_code_lines,
            rate=rate,
            volume=volume,
            cfg=runtime_cfg,
            adapter=tts_adapter,
        )
