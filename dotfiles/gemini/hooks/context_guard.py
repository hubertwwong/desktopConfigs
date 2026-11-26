#!/usr/bin/env python3
"""PreInvocation hook: show a zero-token UI emoji hint when context >= 150k."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

WARN_TOKENS = int(os.environ.get("AGY_CONTEXT_WARN_TOKENS") or 150_000)
STEP_TOKENS = int(os.environ.get("AGY_CONTEXT_STEP_TOKENS") or 50_000)
_TAIL_BYTES = 131_072


def latest_context_tokens(transcript_path: Path) -> int:
    """Return input_tokens + cache_read_tokens from the newest PLANNER_RESPONSE."""
    if not transcript_path.is_file():
        return 0
    try:
        size = transcript_path.stat().st_size
        with transcript_path.open("rb") as fh:
            if size > _TAIL_BYTES:
                fh.seek(-_TAIL_BYTES, os.SEEK_END)
            chunk = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return 0

    for line in reversed(chunk.splitlines()):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if obj.get("type") == "PLANNER_RESPONSE":
            return int(obj.get("input_tokens") or 0) + int(obj.get("cache_read_tokens") or 0)
    return 0


def _milestone_for(tokens: int, warn_tokens: int, step_tokens: int) -> int:
    if tokens < warn_tokens:
        return 0
    step = max(1, step_tokens)
    return warn_tokens + ((tokens - warn_tokens) // step) * step


def _state_file(conv_id: str, state_dir: Path | None = None) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in conv_id) or "default"
    base = state_dir or Path(tempfile.gettempdir())
    return base / f"agy-ctx-guard-{safe}.json"


def _read_last_milestone(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return int(data.get("milestone") or 0) if isinstance(data, dict) else 0
    except (OSError, ValueError):
        return 0


def _banner_step(tokens: int, warn_tokens: int, step_tokens: int) -> dict:
    icon = "🔥🚨" if tokens >= warn_tokens + step_tokens else "🚨🧹"
    banner = (
        f"> {icon} **Context at ~{tokens // 1000}k tokens** — "
        "📝 save `session-note` & 🔄 run `/new` to keep context lean!"
    )
    return {"systemMessage": {"systemMessage": "", "metadata": {"user_markdown": banner}}}


def build_response(
    payload: dict,
    warn_tokens: int = WARN_TOKENS,
    step_tokens: int = STEP_TOKENS,
    state_dir: Path | None = None,
) -> dict:
    """Return UI-only user_markdown warning (empty systemMessage) at 150k+ milestones."""
    raw_transcript = payload.get("transcriptPath")
    if not raw_transcript:
        return {}
    tokens = latest_context_tokens(Path(str(raw_transcript)))
    milestone = _milestone_for(tokens, warn_tokens, step_tokens)
    if milestone <= 0:
        return {}

    conv_id = str(payload.get("conversationId") or "default")
    state_path = _state_file(conv_id, state_dir=state_dir)
    if milestone <= _read_last_milestone(state_path):
        return {}
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"milestone": milestone}) + "\n", encoding="utf-8")
    except OSError:
        return {}
    return {"injectSteps": [_banner_step(tokens, warn_tokens, step_tokens)]}


def main() -> int:
    try:
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {}
        if not isinstance(payload, dict):
            payload = {}
    except (ValueError, OSError):
        payload = {}

    print(json.dumps(build_response(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
