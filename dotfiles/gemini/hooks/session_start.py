#!/usr/bin/env python3
"""SessionStart hook: surface ./ai/session-note.md after /new without auto-running it."""

from datetime import datetime
import json
from pathlib import Path
import sys


def _find_note(payload: dict) -> Path | None:
    candidates = []
    for raw in [payload.get("cwd"), *(payload.get("workspacePaths") or [])]:
        if raw and raw not in candidates:
            candidates.append(raw)
    for base in candidates:
        note = Path(base) / "ai" / "session-note.md"
        if note.is_file() and note.stat().st_size > 0:
            return note
    return None


def _extract_goal(text: str) -> str:
    lines = text.splitlines()
    in_goal = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## goal"):
            in_goal = True
            continue
        if in_goal:
            if stripped.startswith("#"):
                break
            if stripped:
                return stripped[:140]
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:140]
    return "Saved session handoff"


def build_response(payload: dict) -> dict:
    note = _find_note(payload)
    if not note:
        return {}

    try:
        content = note.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    goal = _extract_goal(content)
    mtime = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    rel_hint = "ai/session-note.md"
    return {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": (
                        f"A session handoff note exists at {note} (saved {mtime}). "
                        f"Summary: {goal}. Do NOT read or execute it unless the user "
                        f"asks to resume/continue or references the session note."
                    ),
                    "metadata": {
                        "user_markdown": (
                            f"> **Session note found** (`{rel_hint}`, saved {mtime}): "
                            f"{goal} — type `resume` to continue."
                        )
                    },
                }
            }
        ]
    }


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
