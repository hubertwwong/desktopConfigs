#!/usr/bin/python3
"""Custom Antigravity CLI status line showing context window and token usage."""

import json
import os
import sys

WARN_CONTEXT_TOKENS = int(os.environ.get("AGY_CONTEXT_WARN_TOKENS") or 150_000)


def fmt_tokens(count: float) -> str:
    """Format token counts compactly (e.g., 850, 12.3k, 1.0M)."""
    n = float(count or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(int(n))


def current_context_tokens(cw: dict) -> int:
    """Estimate active context window tokens from current_usage or percentage."""
    curr = cw.get("current_usage") or {}
    curr_sum = (
        int(curr.get("input_tokens") or 0)
        + int(curr.get("cache_read_input_tokens") or 0)
        + int(curr.get("cache_creation_input_tokens") or 0)
    )
    if curr_sum > 0:
        return curr_sum
    used_pct = float(cw.get("used_percentage") or 0.0)
    ctx_size = int(cw.get("context_window_size") or 0)
    if used_pct > 0 and ctx_size > 0:
        return round((used_pct / 100.0) * ctx_size)
    return int(cw.get("total_input_tokens") or 0)


def progress_bar(pct: float, width: int = 10) -> str:
    """Render an ANSI-colored progress bar for context window usage."""
    clamped = max(0.0, min(100.0, pct))
    filled = round((clamped / 100.0) * width)
    bar = "█" * filled + "░" * (width - filled)
    if clamped >= 80.0:
        color = "\033[31m"
    elif clamped >= 50.0:
        color = "\033[33m"
    else:
        color = "\033[32m"
    return f"{color}[{bar}]\033[0m"


def format_status(data: dict, warn_tokens: int = WARN_CONTEXT_TOKENS) -> str:
    """Format status line text with an emoji handoff hint when context >= warn_tokens."""
    cw = data.get("context_window") or {}
    curr = cw.get("current_usage") or {}
    used_pct = float(cw.get("used_percentage") or 0.0)
    ctx_size = int(cw.get("context_window_size") or 0)
    total_in = int(cw.get("total_input_tokens") or 0)
    total_out = int(cw.get("total_output_tokens") or 0)
    cache_read = int(curr.get("cache_read_input_tokens") or 0)
    width = int(data.get("terminal_width") or 100)
    active_ctx = current_context_tokens(cw)

    if active_ctx >= warn_tokens:
        if width < 70:
            return f"🚨🧹 {fmt_tokens(active_ctx)} ({used_pct:.0f}%) │ 📝 session-note → 🔄 /new"
        bar = progress_bar(used_pct)
        size_str = f" ({fmt_tokens(ctx_size)})" if ctx_size > 0 else ""
        return f"🚨🧹 ctx {bar} {used_pct:.1f}%{size_str} · {fmt_tokens(active_ctx)} │ 📝 session-note → 🔄 /new"

    token_parts = [f"{fmt_tokens(total_in)} in", f"{fmt_tokens(total_out)} out"]
    if cache_read > 0:
        token_parts.append(f"{fmt_tokens(cache_read)} cached")
    tokens_str = " · ".join(token_parts)

    if width < 70:
        return f"ctx {used_pct:.1f}% │ {tokens_str}"

    bar = progress_bar(used_pct)
    size_str = f" ({fmt_tokens(ctx_size)})" if ctx_size > 0 else ""
    return f"ctx {bar} {used_pct:.1f}%{size_str} │ tokens: {tokens_str}"


def main() -> None:
    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
    except (ValueError, OSError):
        data = {}
    print(format_status(data if isinstance(data, dict) else {}))


if __name__ == "__main__":
    main()
