---
name: plan-execute
description: >-
  Use this skill to execute an approved implementation plan in ./ai/plan.md, ./ai/plans/<slug>.md,
  or ./ai/plans/<slug>/. Enforces sequential step execution, immediate test verification, and recording mid-course decisions.
---

# Plan Execute Skill

Use this skill to systematically execute an approved plan (`./ai/plan.md`, `./ai/plans/<slug>.md`, or `./ai/plans/<slug>/`).

---

## Mode Handling

- **Flat Plan (`./ai/plan.md` or `./ai/plans/<slug>.md`):** Execute checklist steps sequentially. If the file grows past 10 steps or ~12KB mid-flight, promote remaining unchecked steps into a directory board at `./ai/plans/<slug>/` per `plan-create`.
- **Directory Board (`./ai/plans/<slug>/`):**
  1. Read `OVERVIEW.md` and list `doing/` and `todo/` — **never read `done/`**.
  2. Resume any card already in `doing/` first; otherwise `mv` the next `todo/` card into `doing/` and read only that card.
  3. Update `- [x]` sub-steps inside the card if pausing mid-card; record cross-card changes in `OVERVIEW.md`.
  4. Only after verification passes, `mv` the card from `doing/` to `done/`.

---

## Execution Loop

For each step or card:

1. **Pre-Check Guardrails**:
   - Ensure the upcoming action does not violate any **No-Gos**.
   - If a step cannot be completed without violating a No-Go, stop and notify the user.

2. **Minimal Implementation**:
   - Make only the targeted changes required for the current step/card. Do not skip ahead or bundle unrelated refactors.

3. **Immediate Test Verification**:
   - Run the specified verification command.
   - If the verification fails, diagnose and fix within the step.

4. **Check Off / Advance State**:
   - Flat plan: mark `- [x]` only after verification passes.
   - Directory board: `mv` the card from `doing/` to `done/` only after verification passes.

5. **Log Pivots in Decision Log**:
   - If a technical choice, dependency, or step changes during execution, log it immediately under `## 5. Decision Log & Changes` (in the flat plan or `OVERVIEW.md`):
     ```markdown
     - **YYYY-MM-DD**: <What changed, why, and impact on remaining work>
     ```

6. **Workspace Discipline**:
   - Scratch scripts or exploratory snippets go to `./ai/scratch/` and are never committed to git.
   - Deliverables and guides go to `docs/`.
