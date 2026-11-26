# Global Agent Guidelines

1. **Simple Tasks:** Execute directly and report the result.
2. **Complex / Multi-Step Tasks:** Create `./ai/plan.md` using `plan-create`, check for relevant runbooks in `docs/runbooks/`, and execute sequentially with `plan-execute`.
3. **Workspace Organization:** 
   - `./ai/` is for internal agent work products (scratch scripts, plans, data dumps) and must NEVER be committed to git.
   - `./docs/` is for human deliverables, guides, and runbooks.
4. **Git Auto-Push (Private Personal Repos Only):**
   - For personal projects backed by a **confirmed private** GitHub repository (under `hubertwwong/`, verified via `gh repo view --json isPrivate` or a project-local `AGENTS.md` note), automatically stage, commit, and push completed deliverable changes after verification passes.
   - **Never** commit `./ai/` or secrets/credentials (`.env`, `*.pem`, `*.key`, etc.), **never** force-push, and **never** auto-push to public or shared/org repos without explicit permission.
5. **Session Handoff (`/new` Resume):**
   - Before starting a fresh session with `/new`, use `session-note` when asked to save a handoff note (`./ai/session-note.md`).
   - When resuming or continuing after `/new`, use `session-note` to read `./ai/session-note.md` first.
6. **Human-First Responses:**
   - Write for a human scanning quickly, not another AI: open with a 1–2 sentence plain-English takeaway (what changed, whether it works, and any choice needed), followed by short bullets only when helpful.
   - Skip raw logs, symbol dumps, and internal jargon unless asked; link to files or `./docs/` for details instead of repeating them.
