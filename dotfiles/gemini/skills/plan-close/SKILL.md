---
name: plan-close
description: >-
  Use this skill to close a completed implementation plan in ./ai/plan.md,
  ./ai/plans/<slug>.md, or ./ai/plans/<slug>/. Verifies acceptance criteria,
  runs a micro-retro for process friction, and archives to ./ai/archive/.
---

# Plan Close Skill

Completes verification, captures high-leverage process improvements, summarizes receipts for user review, and archives the finished plan.

## Plan Close Protocol

1. **Acceptance Verification**:
   - Confirm every checklist item is `[x]` (or `todo/` and `doing/` are empty).
   - Run full end-to-end acceptance/regression commands and verify every Acceptance Criterion passes.

2. **Micro-Retro (Capture Friction)**:
   - Check if anything caused repeated rework, missed checks, or silent assumptions during execution.
   - If mechanical (linting, file limits, git/secret guard), propose a **deterministic script/hook**; if a judgement call, propose a **1-line skill or `AGENTS.md` edit**. Skip if execution was smooth.

3. **Summarize for User Audit**:
   - Present a concise closeout: **Delivered Changes**, **Verification Receipts**, **Decisions Logged**, and any **Micro-Retro Proposal**.
   - Invite user audit before archiving.

4. **Archive Plan**:
   - Upon signoff: `mkdir -p ./ai/archive` and move `./ai/plan.md` (or `./ai/plans/<slug>*`) to `./ai/archive/<YYYY-MM-DD>_<slug>.md` (or directory).
   - Confirm the active plan path is clear.
