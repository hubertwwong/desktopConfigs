#!/usr/bin/python3
"""Custom Antigravity CLI status line showing context window and token usage."""

import json
import sys


def fmt_tokens(count: float) -> str:
    """Format token counts compactly (e.g., 850, 12.3k, 1.0M)."""
    n = float(count or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(int(n))


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


def main() -> None:
    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
    except Exception:
        data = {}

    cw = data.get("context_window") or {}
    curr = cw.get("current_usage") or {}

    used_pct = float(cw.get("used_percentage") or 0.0)
    ctx_size = int(cw.get("context_window_size") or 0)
    total_in = int(cw.get("total_input_tokens") or 0)
    total_out = int(cw.get("total_output_tokens") or 0)
    cache_read = int(curr.get("cache_read_input_tokens") or 0)
    width = int(data.get("terminal_width") or 100)

    token_parts = [f"{fmt_tokens(total_in)} in", f"{fmt_tokens(total_out)} out"]
    if cache_read > 0:
        token_parts.append(f"{fmt_tokens(cache_read)} cached")
    tokens_str = " · ".join(token_parts)

    if width < 70:
        print(f"ctx {used_pct:.1f}% │ {tokens_str}")
        return

    bar = progress_bar(used_pct)
    size_str = f" ({fmt_tokens(ctx_size)})" if ctx_size > 0 else ""
    print(f"ctx {bar} {used_pct:.1f}%{size_str} │ tokens: {tokens_str}")


if __name__ == "__main__":
    main()
