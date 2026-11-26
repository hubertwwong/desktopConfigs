---
name: assistant
description: >-
  Use this skill when the user asks what they have been working on across
  projects, asks to resume another project from the home directory, or wants to
  check or update cross-project todos and high-level personal memory.
---

# Personal Assistant Skill

Provides a lightweight, low-token cross-project radar backed by `${AGY_ASSISTANT_DIR:-~/projects/personal-assistant}` while keeping project-specific details inside each project.

---

## Ground Rules
- **High-Level Only**: Never copy project-specific plans, code details, or transcript dumps into `personal-assistant`.
- **Live State Over Stale Memory**: Always run `scan_projects.py` to inspect sibling projects in `${AGY_PROJECTS_DIR:-~/projects}` instead of trusting memory alone.
- **No-Op Gracefully**: If `${AGY_ASSISTANT_DIR:-~/projects/personal-assistant}` does not exist on the machine, inform the user instead of failing silently.

---

## Mode 1: Resume Another Project (`"resume <project>"`)

1. **Fetch Live Recap**:
   ```bash
   python3 "${AGY_ASSISTANT_DIR:-$HOME/projects/personal-assistant}/scripts/scan_projects.py" --project "<name>"
   ```
   *(If unsure of exact folder name, run with `--compact` first.)*
2. **Inspect Target Ground Truth (Read-Only)**:
   - If `session-note` exists in `<project>/ai/session-note.md`, read it to confirm **Goal** and **Next Step**.
3. **Recap & Recommend Clean Handoff**:
   - Present a 3–5 line recap (branch/dirty status, last goal, next step, active plan).
   - Recommend launching inside the target workspace for full `AGENTS.md`, hooks, and `./ai/` isolation:
     ```bash
     cd <project-path> && agy
     ```
   - Only continue working from `~` if the user explicitly asks for a quick one-off check here.

---

## Mode 2: Cross-Project Status (`"what have I been working on?"`)

1. Run:
   ```bash
   python3 "${AGY_ASSISTANT_DIR:-$HOME/projects/personal-assistant}/scripts/scan_projects.py" --compact
   ```
2. Read `${AGY_ASSISTANT_DIR:-~/projects/personal-assistant}/todos.md` and `memory.md` (and latest `log/YYYY-MM.md` if relevant).
3. Summarize active todos, recently touched projects, and any paused context in under 10 lines.

---

## Mode 3: Update Todos or High-Level Memory

1. Edit `${AGY_ASSISTANT_DIR:-~/projects/personal-assistant}/todos.md` (`Active`, `Waiting`, `Done`) or `memory.md` (keep 1-line entries; keep `memory.md` concise).
2. Optionally append a 1-line milestone to `log/YYYY-MM.md` when major cross-project work wraps up.
3. Verify with `git -C "${AGY_ASSISTANT_DIR:-$HOME/projects/personal-assistant}" diff` and report the updated lines.
