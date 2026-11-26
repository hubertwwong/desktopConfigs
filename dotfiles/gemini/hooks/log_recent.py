#!/usr/bin/env python3
"""Stop hook: record lightweight per-cwd breadcrumbs into personal-assistant."""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys

MAX_ENTRIES = 10
MAX_HINT_LEN = 80
_META_BLOCK_RE = re.compile(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", re.DOTALL)
_TAG_RE = re.compile(r"</?(?:USER_REQUEST|ADDITIONAL_METADATA)>")


def _assistant_dir() -> Path:
    raw = os.environ.get("AGY_ASSISTANT_DIR")
    return Path(raw).expanduser() if raw else Path.home() / "projects" / "personal-assistant"


def _clean_hint(raw: str) -> str:
    text = _META_BLOCK_RE.sub(" ", raw or "")
    text = _TAG_RE.sub(" ", text)
    compact = " ".join(text.split())
    if len(compact) > MAX_HINT_LEN:
        return compact[: MAX_HINT_LEN - 3].rstrip() + "..."
    return compact


def _is_ignored_cwd(cwd: Path, home: Path) -> bool:
    if cwd == home or cwd.is_relative_to(home):
        return False
    s = str(cwd)
    return s == "/tmp" or s.startswith("/tmp/") or s == "/var/tmp" or s.startswith("/var/tmp/")


def _project_label(cwd: Path, home: Path) -> str:
    if cwd == home:
        return "~"
    projects_root = (home / "projects").resolve()
    try:
        rel = cwd.relative_to(projects_root)
        return rel.parts[0] if rel.parts else cwd.name
    except ValueError:
        return cwd.name or str(cwd)


def record_stop(payload: dict, assistant_dir: Path | None = None, home: Path | None = None) -> bool:
    """Update recent.json with one compact breadcrumb per cwd. Returns True if written."""
    if payload.get("continuationActive"):
        return False
    raw_cwd = payload.get("cwd")
    if not raw_cwd:
        return False

    base = assistant_dir or _assistant_dir()
    if not base.is_dir():
        return False

    home_dir = (home or Path.home()).resolve()
    cwd = Path(raw_cwd).resolve()
    if _is_ignored_cwd(cwd, home_dir) or not cwd.is_dir():
        return False

    hint = _clean_hint(str(payload.get("lastUserInput") or ""))
    if not hint:
        return False

    state_file = base / "state" / "recent.json"
    existing: list[dict] = []
    if state_file.is_file():
        try:
            loaded = json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
            if isinstance(loaded, list):
                existing = [e for e in loaded if isinstance(e, dict) and e.get("cwd") != str(cwd)]
        except (OSError, ValueError):
            existing = []

    now = datetime.now()
    entry = {
        "project": _project_label(cwd, home_dir),
        "cwd": str(cwd),
        "hint": hint,
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
        "ts": round(now.timestamp(), 3),
    }
    updated = [entry, *existing][:MAX_ENTRIES]

    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file = state_file.with_suffix(".json.tmp")
        tmp_file.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_file, state_file)
    except OSError:
        return False
    return True


def main() -> int:
    try:
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {}
        if not isinstance(payload, dict):
            payload = {}
    except (ValueError, OSError):
        payload = {}

    record_stop(payload)
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
