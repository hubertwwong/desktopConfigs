#!/usr/bin/env python3
"""SessionStart hook: surface ./ai/session-note.md and (in ~) a tiny assistant radar."""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys


def _assistant_dir() -> Path:
    raw = os.environ.get("AGY_ASSISTANT_DIR")
    return Path(raw).expanduser() if raw else Path.home() / "projects" / "personal-assistant"


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


def _read_active_todos(todos_file: Path, limit: int = 3) -> tuple[int, list[str]]:
    if not todos_file.is_file():
        return 0, []
    try:
        lines = todos_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return 0, []
    in_active = False
    items: list[str] = []
    for raw in lines:
        s = raw.strip()
        if s.lower().startswith("## active"):
            in_active = True
            continue
        if in_active and s.startswith("## "):
            break
        if in_active and s.startswith("- [ ] "):
            items.append(s[6:].replace("`", "").strip()[:60])
    return len(items), items[:limit]


def _read_recent_projects(recent_file: Path, limit: int = 3) -> list[str]:
    if not recent_file.is_file():
        return []
    try:
        data = json.loads(recent_file.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    out: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        proj = str(item.get("project") or "").strip()
        if proj and proj != "~":
            out.append(proj)
        if len(out) >= limit:
            break
    return out


def _build_home_radar(
    payload: dict,
    assistant_dir: Path | None = None,
    home: Path | None = None,
) -> dict | None:
    raw_cwd = payload.get("cwd")
    if not raw_cwd:
        return None
    home_dir = (home or Path.home()).resolve()
    try:
        if Path(raw_cwd).resolve() != home_dir:
            return None
    except OSError:
        return None

    base = assistant_dir or _assistant_dir()
    if not base.is_dir():
        return None

    todo_count, top_todos = _read_active_todos(base / "todos.md")
    recent = _read_recent_projects(base / "state" / "recent.json")
    if not todo_count and not recent:
        return None

    parts = []
    if todo_count:
        parts.append(f"Todos ({todo_count}): " + "; ".join(top_todos))
    if recent:
        parts.append("Recent: " + ", ".join(recent))
    summary = " | ".join(parts)

    return {
        "systemMessage": {
            "systemMessage": (
                f"Background assistant radar ({base}): {summary}. "
                "Use the `assistant` skill only if the user asks about tasks, memory, or resuming a project."
            ),
            "metadata": {"user_markdown": f"> **Assistant radar:** {summary}"},
        }
    }


def build_response(
    payload: dict,
    assistant_dir: Path | None = None,
    home: Path | None = None,
) -> dict:
    steps: list[dict] = []

    note = _find_note(payload)
    if note:
        try:
            content = note.read_text(encoding="utf-8", errors="replace")
            goal = _extract_goal(content)
            mtime = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            steps.append(
                {
                    "systemMessage": {
                        "systemMessage": (
                            f"A session handoff note exists at {note} (saved {mtime}). "
                            f"Summary: {goal}. Do NOT read or execute it unless the user "
                            "asks to resume/continue or references the session note."
                        ),
                        "metadata": {
                            "user_markdown": (
                                f"> **Session note found** (`ai/session-note.md`, saved {mtime}): "
                                f"{goal} — type `resume` to continue."
                            )
                        },
                    }
                }
            )
        except OSError:
            pass

    radar = _build_home_radar(payload, assistant_dir=assistant_dir, home=home)
    if radar:
        steps.append(radar)

    return {"injectSteps": steps} if steps else {}


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
