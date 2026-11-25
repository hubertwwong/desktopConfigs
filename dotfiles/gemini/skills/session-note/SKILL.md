---
name: session-note
description: >-
  Use this skill when the user asks to save a session handoff note before /new
  (avoiding context compression) or asks to resume/continue from a saved
  session note in a new session.
---

# Session Note Skill

Replaces lossy context compression with an explicit handoff file at `./ai/session-note.md` that survives `/new`.

---

## Mode 1: Save Handoff Note (Before `/new`)

Activate when the user says *"save session note"*, *"write handoff"*, *"prep for /new"*, or invokes `/session-note`.

1. **Gather Ground Truth**
   - If inside a git repository, run `git status --short && git log -1 --oneline` so the note records exact verified state.
   - Check whether `./ai/plan.md` or `./ai/plans/` exists and note the active plan path and current step (or `doing/` + `todo/` card names).

2. **Archive Prior Note (If Present)**
   - If `./ai/session-note.md` already exists, move it to `./ai/archive/<YYYY-MM-DD_HHMM>_session-note.md` first (`mkdir -p ./ai/archive`).

3. **Write `./ai/session-note.md` (Keep Under 45 Lines)**
   Use this exact structure—facts only, no transcript dump:

   ```markdown
   # Session Note (<YYYY-MM-DD HH:MM>)
   Workspace: <cwd>

   ## Goal
   <1-2 sentences on what we are trying to accomplish.>

   ## Current State
   - Branch / Commit: <branch @ sha> (or N/A)
   - Working Tree: <clean or modified files>
   - Checks: <last test/build command and exact result>
   - Active Plan: <./ai/plan.md step status or none>

   ## Decisions & Gotchas
   - <Only non-obvious constraints, user preferences, or traps the next session must not repeat>

   ## Files Changed
   - `<path>`: <1-line summary>

   ## Next Step
   <Exact first command, edit, or question to start with after /new.>
   ```

4. **Verify**
   - Confirm `./ai/session-note.md` is non-empty and, if inside a git repo, check `git check-ignore -q ai/` (warn the user if `ai/` is not gitignored).
   - Tell the user the handoff is saved and they can run `/new` (and type `resume` in the new session).

---

## Mode 2: Resume Session (After `/new`)

Activate when the user says *"resume"*, *"continue"*, *"pick up where we left off"*, or `/session-note resume`.

1. **Read Handoff State**
   - Read `./ai/session-note.md`. If missing, check `./ai/archive/` for the newest `*_session-note.md` or inform the user no session note was found.
   - If `./ai/session-note.md` references `./ai/plan.md` or `./ai/plans/<slug>`, read the flat plan—or for a directory board, read `OVERVIEW.md` and list `doing/` / `todo/` (skip `done/`).

2. **Sanity-Check Workspace**
   - If in a git repo, run `git status --short && git log -1 --oneline` to confirm the workspace still matches the saved state.

3. **Recap & Execute**
   - Present a 3–4 line summary (Goal, Current State, Proposed Next Step).
   - Immediately proceed with **Next Step** unless it is destructive, ambiguous, or contradicts a new instruction from the user.
