from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    min_paragraphs: int = 4
    min_new_code_lines: int = 100
    enabled: bool = True
    rate: int = 0
    volume: int = 100
    async_speech: bool = True


def _parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(raw: str | None, default: int) -> int:
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def load_config() -> RuntimeConfig:
    return RuntimeConfig(
        min_paragraphs=_parse_int(os.getenv("MCP_TTS_SUMMARY_MIN_PARAGRAPHS"), 4),
        min_new_code_lines=_parse_int(os.getenv("MCP_TTS_SUMMARY_MIN_NEW_CODE_LINES"), 100),
        enabled=_parse_bool(os.getenv("MCP_TTS_SUMMARY_ENABLED"), True),
        rate=_parse_int(os.getenv("MCP_TTS_SUMMARY_RATE"), 0),
        volume=_parse_int(os.getenv("MCP_TTS_SUMMARY_VOLUME"), 100),
        async_speech=_parse_bool(os.getenv("MCP_TTS_SUMMARY_ASYNC_SPEECH"), True),
    )
