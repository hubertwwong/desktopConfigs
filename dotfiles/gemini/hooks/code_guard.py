#!/usr/bin/env python3
"""Deterministic AST & size guardrails against bloated or sloppy agent code."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import subprocess
import sys

MAX_PY_LINES = 300
MAX_SH_LINES = 25
MAX_FUNC_LINES = 40
MAX_NESTING = 4
_SKIP_PREFIXES = ("ai/", ".agents/", "node_modules/", ".venv/", "venv/", "evals/fixtures/")
_CONTROL_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)


def _should_skip(rel_path: str) -> bool:
    norm = rel_path.replace("\\", "/").lstrip("./")
    if any(norm.startswith(p) or f"/{p}" in norm for p in _SKIP_PREFIXES):
        return True
    return not (norm.endswith(".py") or norm.endswith(".sh"))


def _has_allow(lines: list[str], lineno: int | None = None) -> bool:
    if any("code-guard:allow" in line for line in lines[:5]):
        return True
    if lineno is not None and 1 <= lineno <= len(lines):
        window = lines[max(0, lineno - 2) : lineno]
        return any("code-guard:allow" in line for line in window)
    return False


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        next_depth = depth + 1 if isinstance(child, _CONTROL_NODES) else depth
        best = max(best, _max_nesting(child, next_depth))
    return best


def _inspect_python(source: str, lines: list[str]) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    if len(lines) > MAX_PY_LINES and not _has_allow(lines):
        findings.append(("file_bloat", f"{len(lines)} lines > {MAX_PY_LINES}"))
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [*findings, ("syntax_error", f"line {exc.lineno}: {exc.msg}")]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _has_allow(lines, node.lineno):
                continue
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > MAX_FUNC_LINES:
                findings.append(("long_func", f"{node.name} ({length}L > {MAX_FUNC_LINES})"))
            nesting = _max_nesting(node)
            if nesting > MAX_NESTING:
                findings.append(("deep_nesting", f"{node.name} (depth {nesting} > {MAX_NESTING})"))
        elif isinstance(node, ast.ExceptHandler):
            if _has_allow(lines, node.lineno):
                continue
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                findings.append(("silent_except", f"line {node.lineno}: except ...: pass"))
    return findings


def inspect_source(source: str, rel_path: str) -> list[tuple[str, str]]:
    """Return list of (kind, detail) violations for Python or shell source."""
    lines = source.splitlines()
    if rel_path.endswith(".sh"):
        if len(lines) > MAX_SH_LINES and not _has_allow(lines):
            return [("bash_bloat", f"{len(lines)} lines > {MAX_SH_LINES}")]
        return []
    if rel_path.endswith(".py"):
        return _inspect_python(source, lines)
    return []


def _git_output(repo: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    return proc.stdout if proc.returncode == 0 else ""


def _head_findings(repo: Path, rel_path: str) -> list[tuple[str, str]]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{rel_path}"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return []
    return inspect_source(proc.stdout, rel_path)


def _new_violations(repo: Path, rel_path: str, source: str) -> list[str]:
    cur = inspect_source(source, rel_path)
    if not cur:
        return []
    prev_keys = {(k, d.split(" ", 1)[0]) for k, d in _head_findings(repo, rel_path)}
    out: list[str] = []
    for kind, detail in cur:
        key = (kind, detail.split(" ", 1)[0])
        if kind == "file_bloat" and ("file_bloat", "") in {(k, "") for k, _ in prev_keys}:
            head_lines = len(_git_output(repo, ["show", f"HEAD:{rel_path}"]).splitlines())
            if len(source.splitlines()) <= head_lines:
                continue
        elif kind != "file_bloat" and key in prev_keys:
            continue
        out.append(f"{rel_path}: {kind} - {detail}")
    return out


def check_working_tree(repo: Path) -> list[str]:
    """Check dirty/untracked files in repo against HEAD baseline."""
    status = _git_output(repo, ["status", "--porcelain"])
    violations: list[str] = []
    for line in status.splitlines():
        if len(line) <= 3 or line.startswith("D ") or line.startswith(" D"):
            continue
        rel = line[3:].strip().split(" -> ")[-1]
        if _should_skip(rel):
            continue
        target = repo / rel
        if target.is_file():
            text = target.read_text(encoding="utf-8", errors="replace")
            violations.extend(_new_violations(repo, rel, text))
    return violations


def check_staged(repo: Path) -> list[str]:
    """Check staged files in repo against HEAD baseline."""
    names = _git_output(repo, ["diff", "--cached", "--name-only", "--diff-filter=ACM"])
    violations: list[str] = []
    for rel in names.splitlines():
        rel = rel.strip()
        if not rel or _should_skip(rel):
            continue
        staged_src = _git_output(repo, ["show", f":{rel}"])
        if staged_src:
            violations.extend(_new_violations(repo, rel, staged_src))
    return violations


def handle_stop(payload: dict) -> dict:
    """Handle AGY Stop hook JSON payload safely without looping."""
    if payload.get("continuationActive"):
        return {}
    reason = str(payload.get("terminationReason") or "")
    if reason and reason != "NO_TOOL_CALL":
        return {}
    cwd = payload.get("cwd")
    if not cwd:
        return {}
    repo = Path(cwd)
    if not (repo / ".git").exists():
        return {}
    violations = check_working_tree(repo)
    if not violations:
        return {}
    summary = "\n".join(f"- {v}" for v in violations[:8])
    return {
        "decision": "continue",
        "reason": f"code_guard detected new structural violations:\n{summary}\nRefactor or add `# code-guard:allow` if intentional.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic AST and size code guardrail.")
    parser.add_argument("--mode", choices=["check", "stop", "pre-commit"], default="check")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)

    if args.mode == "stop":
        try:
            raw = sys.stdin.read().strip()
            payload = json.loads(raw) if raw else {}
        except (ValueError, OSError):
            payload = {}
        print(json.dumps(handle_stop(payload if isinstance(payload, dict) else {})))
        return 0

    if args.mode == "pre-commit":
        violations = check_staged(args.repo)
    elif args.files:
        violations = [
            f"{f}: {k} - {d}"
            for f in args.files
            if Path(f).is_file()
            for k, d in inspect_source(Path(f).read_text(encoding="utf-8", errors="replace"), f)
        ]
    else:
        violations = check_working_tree(args.repo)

    for v in violations:
        print(f"[code-guard] {v}", file=sys.stderr)
    return 1 if (violations and not args.warn_only) else 0


if __name__ == "__main__":
    raise SystemExit(main())
