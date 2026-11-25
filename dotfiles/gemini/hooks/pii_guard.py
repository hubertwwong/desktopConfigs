#!/usr/bin/env python3
"""Shared PII & secret guard for AGY PreToolUse and global git hooks.

Modes:
  --mode agy         Read AGY PreToolUse JSON from stdin; emit allow/deny/force_ask JSON.
  --mode pre-commit  Scan staged git changes; exit 1 on hard blocks.
  --mode pre-push    Scan unpushed commits (stdin ref lines); exit 1 on hard blocks.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ZERO_SHA = "0" * 40
ALLOW_MARKER = "pii-guard:allow"
ALLOWED_ENV_NAMES = {".env.example", ".env.sample", ".env.template"}
FORBIDDEN_PATH_RE = re.compile(
    r"(?:^ai(?:/|$)|(?:^|/)(?:\.env(?:\.(?!example$|sample$|template$)[^/]+)?$|.*\.pem$|.*\.key$|.*\.kdbx$|.*\.pgp$|.*\.gpg$|auth\.json$))"
)

FALLBACK_SECRET_RES = [
    ("pem-private-key", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("generic-sk-token", re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9\-_]{24,}\b")),
]

SSN_RE = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
CC_CANDIDATE_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")
PRIVATE_IP_RE = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3})\b"
)


@dataclass
class ScanReport:
    hard: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)


def luhn_valid(digits: str) -> bool:
    """Return True if a 13-19 digit string passes the Luhn check."""
    if not (13 <= len(digits) <= 19) or not digits.isdigit():
        return False
    if len(set(digits)) == 1:
        return False
    total = 0
    for idx, ch in enumerate(reversed(digits)):
        n = int(ch)
        if idx % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def load_rule_file(path: Path) -> list[re.Pattern[str]]:
    """Load literal or `re:` patterns from an untracked config file."""
    if not path.is_file():
        return []
    patterns: list[re.Pattern[str]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            patterns.append(re.compile(line[3:].strip()))
        else:
            patterns.append(re.compile(re.escape(line)))
    return patterns


def resolve_gitleaks() -> str | None:
    """Find a runnable gitleaks binary (handling mise shims)."""
    direct = Path.home() / ".local" / "share" / "mise" / "installs" / "gitleaks" / "latest" / "gitleaks"
    if direct.is_file() and os.access(direct, os.X_OK):
        return str(direct)
    found = shutil.which("gitleaks")
    if found:
        probe = subprocess.run([found, "version"], capture_output=True, text=True, timeout=3)
        if probe.returncode == 0:
            return found
    return None


def find_git_root(cwd: str) -> Path | None:
    res = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return Path(res.stdout.strip())
    return None


def extract_added_lines(diff_text: str) -> list[tuple[str, str]]:
    """Return (filepath, added_line) pairs from unified diff output."""
    current_file = "<diff>"
    added: list[tuple[str, str]] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added.append((current_file, line[1:]))
    return added


def scan_diff_and_paths(
    paths: list[str],
    diff_text: str,
    config_dir: Path | None = None,
    use_gitleaks_stdin: bool = False,
) -> ScanReport:
    """Scan changed file paths and unified diff added lines for secrets and PII."""
    report = ScanReport()
    cfg = config_dir or (Path.home() / ".config" / "pii-guard")
    custom_patterns = load_rule_file(cfg / "patterns.txt")
    allow_patterns = load_rule_file(cfg / "allowlist.txt")

    for rel in paths:
        norm = rel.strip().removeprefix("./")
        if not norm:
            continue
        base = Path(norm).name
        if base in ALLOWED_ENV_NAMES:
            continue
        if FORBIDDEN_PATH_RE.search(norm):
            report.hard.append(f"forbidden path: {norm}")

    added_lines = extract_added_lines(diff_text)
    for filepath, text in added_lines:
        if ALLOW_MARKER in text or "#gitleaks:allow" in text:
            continue
        if any(p.search(text) for p in allow_patterns):
            continue

        for name, rx in FALLBACK_SECRET_RES:
            if rx.search(text):
                report.hard.append(f"secret ({name}) in {filepath}")

        for pat in custom_patterns:
            if pat.search(text):
                report.hard.append(f"custom PII pattern in {filepath}")

        if SSN_RE.search(text):
            report.hard.append(f"US SSN pattern in {filepath}")

        for match in CC_CANDIDATE_RE.finditer(text):
            digits = re.sub(r"[ -]", "", match.group(0))
            if luhn_valid(digits):
                report.hard.append(f"payment card pattern in {filepath}")
                break

        if EMAIL_RE.search(text):
            report.soft.append(f"email address in {filepath}")
        if PHONE_RE.search(text):
            report.soft.append(f"phone number in {filepath}")
        if PRIVATE_IP_RE.search(text):
            report.soft.append(f"private/Tailscale IP in {filepath}")

    if use_gitleaks_stdin and added_lines:
        gitleaks = resolve_gitleaks()
        if gitleaks:
            payload = "\n".join(line for _, line in added_lines)
            res = subprocess.run(
                [gitleaks, "stdin", "--no-banner", "--redact", "--exit-code", "1"],
                input=payload,
                capture_output=True,
                text=True,
                timeout=8,
            )
            if res.returncode == 1:
                report.hard.append("gitleaks detected a potential secret in diff")

    report.hard = list(dict.fromkeys(report.hard))
    report.soft = list(dict.fromkeys(report.soft))
    return report


def run_gitleaks_git(repo: Path, args: list[str]) -> str | None:
    """Run gitleaks git subcommand; return finding summary if leaks found."""
    gitleaks = resolve_gitleaks()
    if not gitleaks:
        return None
    cmd = [gitleaks, "git", *args, "--no-banner", "--redact", "--exit-code", "1", str(repo)]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
    if res.returncode == 1:
        lines = [ln.strip() for ln in (res.stdout + "\n" + res.stderr).splitlines() if "RuleID" in ln or "File:" in ln]
        detail = "; ".join(lines[:4]) if lines else "secret detected"
        return f"gitleaks: {detail}"
    return None


def git_output(repo: Path, args: list[str]) -> str:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else ""


def scan_staged(repo: Path) -> ScanReport:
    paths = git_output(repo, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"]).splitlines()
    diff_text = git_output(repo, ["diff", "--cached", "-U0"])
    report = scan_diff_and_paths(paths, diff_text, use_gitleaks_stdin=False)
    leak = run_gitleaks_git(repo, ["--pre-commit", "--staged"])
    if leak:
        report.hard.insert(0, leak)
    return report


def scan_push_ranges(repo: Path, ranges: list[str]) -> ScanReport:
    if not ranges:
        upstream = git_output(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]).strip()
        ranges = [f"{upstream}..HEAD"] if upstream else ["HEAD"]

    all_paths: list[str] = []
    diffs: list[str] = []
    report = ScanReport()
    for rng in ranges:
        if ".." in rng:
            all_paths.extend(git_output(repo, ["diff", "--name-only", "--diff-filter=ACMR", rng]).splitlines())
            diffs.append(git_output(repo, ["diff", "-U0", rng]))
            leak = run_gitleaks_git(repo, [f"--log-opts={rng}"])
        else:
            all_paths.extend(git_output(repo, ["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", rng]).splitlines())
            diffs.append(git_output(repo, ["show", "--format=", "-U0", rng]))
            leak = run_gitleaks_git(repo, [f"--log-opts={rng}"])
        if leak:
            report.hard.append(leak)

    sub = scan_diff_and_paths(all_paths, "\n".join(diffs), use_gitleaks_stdin=False)
    report.hard = list(dict.fromkeys(report.hard + sub.hard))
    report.soft = sub.soft
    return report


def parse_agy_git_intent(command: str, default_cwd: str) -> tuple[str | None, Path]:
    """Return ('commit'|'push'|None, target_dir) for an AGY run_command string."""
    if not re.search(r"\b(?:git|sync-agy|sync-pi)\b", command):
        return None, Path(default_cwd)

    target = Path(default_cwd)
    try:
        tokens = shlex.split(command)
        for i, tok in enumerate(tokens):
            if tok == "-C" and i + 1 < len(tokens):
                target = Path(tokens[i + 1]).expanduser()
                break
    except ValueError:
        pass

    if re.search(r"\b(?:sync-agy|sync-pi)\s+push\b", command):
        return "push", Path.home() / "projects" / "desktopConfigs"
    if re.search(r"\bgit\b[^\n]*\bpush\b", command):
        return "push", target
    if re.search(r"\bgit\b[^\n]*\bcommit\b", command):
        return "commit", target
    return None, target


def handle_agy(payload: dict) -> dict:
    tool_call = payload.get("toolCall") or {}
    args = tool_call.get("args") or {}
    command = args.get("CommandLine") or args.get("command") or ""
    cwd = payload.get("cwd") or os.getcwd()

    intent, target_dir = parse_agy_git_intent(command, cwd)
    if not intent:
        return {"decision": "allow"}

    repo = find_git_root(str(target_dir))
    if not repo:
        return {"decision": "allow"}

    report = scan_staged(repo) if intent == "commit" else scan_push_ranges(repo, [])
    if report.hard:
        return {
            "decision": "deny",
            "reason": "PII/secret guard blocked command: " + "; ".join(report.hard[:5]),
        }
    if report.soft:
        return {
            "decision": "force_ask",
            "reason": "Potential PII detected in diff (" + "; ".join(report.soft[:4]) + "). Confirm before proceeding.",
        }
    return {"decision": "allow"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["agy", "pre-commit", "pre-push"], required=True)
    args = parser.parse_args()

    if args.mode == "agy":
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {}
        print(json.dumps(handle_agy(payload)))
        return 0

    repo = find_git_root(os.getcwd())
    if not repo:
        return 0

    if args.mode == "pre-commit":
        report = scan_staged(repo)
    else:
        ranges: list[str] = []
        for line in sys.stdin.read().splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            _, local_sha, _, remote_sha = parts[:4]
            if local_sha == ZERO_SHA:
                continue
            ranges.append(local_sha if remote_sha == ZERO_SHA else f"{remote_sha}..{local_sha}")
        if not ranges:
            return 0
        report = scan_push_ranges(repo, ranges)

    if report.soft:
        print("[pii-guard] notice: " + "; ".join(report.soft[:5]), file=sys.stderr)
        if os.environ.get("PII_GUARD_STRICT") == "1":
            report.hard.extend(report.soft)

    if report.hard:
        print("[pii-guard] BLOCKED: " + "; ".join(report.hard[:5]), file=sys.stderr)
        print("[pii-guard] Add `# pii-guard:allow` or ~/.config/pii-guard/allowlist.txt for false positives.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
