# MCP TTS Copilot Summary

Python MCP server for Windows text-to-speech that reads existing Copilot summaries using SAPI voice fallback.

## Behavior Summary

- Exposes two MCP tools:
  - `speak_text`
  - `speak_existing_summary`
- Consumes already-prepared summary text (no extra summarization pipeline).
- Trigger strategy is MCP-only and instruction-driven.
- Voice fallback policy:
  1. Use Zira if available.
  2. Else use first available SAPI voice.
  3. If no SAPI voice is available, return non-fatal `skipped` with warning.
- Speech call behavior is non-blocking by default (`MCP_TTS_SUMMARY_ASYNC_SPEECH=true`), so Copilot can continue responding immediately.

## Install

### pip

```powershell
python -m pip install -e .
```

### uv

```powershell
uv pip install -e .
```

## Run

```powershell
python -m mcp_tts_copilot_summary.main
```

Uses stdio transport.

## Configuration

Environment variables:

- `MCP_TTS_SUMMARY_ENABLED` (default: `true`)
- `MCP_TTS_SUMMARY_MIN_PARAGRAPHS` (default: `4`)
- `MCP_TTS_SUMMARY_MIN_NEW_CODE_LINES` (default: `100`)
- `MCP_TTS_SUMMARY_RATE` (default: `0`)
- `MCP_TTS_SUMMARY_VOLUME` (default: `100`)
- `MCP_TTS_SUMMARY_ASYNC_SPEECH` (default: `true`)

Guard criteria used by tools:

- Speak only when `paragraph_count > 4` OR `new_code_lines > 100`.
- If metadata is not provided, tools proceed unless disabled.

## VS Code MCP Registration (Example)

See [examples/mcp.json](examples/mcp.json) for a complete sample.
If `mcp-tts-copilot-summary` is not on `PATH`, prefer launching with `python -m mcp_tts_copilot_summary.main`.

For this workspace on Windows, use:

```json
{
  "mcpServers": {
    "tts-copilot-summary": {
      "command": "python",
      "args": ["-m", "mcp_tts_copilot_summary.main"],
      "env": {
        "MCP_TTS_SUMMARY_ENABLED": "true",
        "MCP_TTS_SUMMARY_MIN_PARAGRAPHS": "4",
        "MCP_TTS_SUMMARY_MIN_NEW_CODE_LINES": "100",
        "MCP_TTS_SUMMARY_RATE": "0",
        "MCP_TTS_SUMMARY_VOLUME": "100"
      }
    }
  }
}
```

This same config is also available at:

- `examples/mcp.json`
- `.vscode/mcp.json`

## Agent Instruction Snippet

Use this policy in your agent instructions:

```md
Call `speak_existing_summary` (or `speak_text`) only when:
- response has more than 4 paragraphs, OR
- response introduces more than 100 new code lines.

Pass existing summary text directly as `summary_text`.
Do not generate a second summary for TTS.
```

Also see [examples/agent-instruction.md](examples/agent-instruction.md).

## Verification

```powershell
python -m pip install -e .
pytest -q
```

## Publish to PyPI

This package is ready for both `pip` and `uv` once published on PyPI.

1. Create a GitHub repository and push this project.
2. In GitHub repository settings, configure trusted publishing for PyPI.
3. Create a GitHub release tag like `v0.1.0`.
4. The workflow at `.github/workflows/publish.yml` builds and publishes automatically.

After publication, installation works globally with either tool:

```powershell
python -m pip install mcp-tts-copilot-summary
uv pip install mcp-tts-copilot-summary
```

Manual checks:

1. Start MCP server and run `tools/list`.
2. Confirm `speak_text` and `speak_existing_summary` are listed.
3. Invoke either tool with sample summary text.
4. Confirm Zira is used when available, otherwise first SAPI voice, otherwise `skipped` warning.

### Copy-Ready Smoke Calls

Expected to speak:

```json
{
  "summary_text": "This is a test summary for speech output.",
  "paragraph_count": 5,
  "new_code_lines": 0
}
```

Expected to skip (threshold not met):

```json
{
  "summary_text": "Short summary.",
  "paragraph_count": 2,
  "new_code_lines": 10
}
```
