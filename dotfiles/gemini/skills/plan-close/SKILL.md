---
name: plan-close
description: >-
  Use this skill to complete and close an implementation plan in ./ai/plan.md, ./ai/plans/<slug>.md,
  or ./ai/plans/<slug>/. Verifies all acceptance criteria, summarizes final receipts for user audit, and archives to ./ai/archive/.
---

# Plan Close Skill

Use this skill when all steps in the active plan have been executed. It handles final verification, solicits user audit/review, and cleanly archives the completed plan.

---

## Plan Close Protocol

1. **Acceptance Verification**:
   - Inspect all items in `## 4. Acceptance Criteria` (flat plan or `OVERVIEW.md`).
   - Run full end-to-end regression/acceptance tests to confirm every criterion passes.
   - Ensure all checklist steps are marked `- [x]` (flat plan) or `todo/` and `doing/` are empty (directory board).

2. **Summarize for User Audit**:
   - Present a concise, two-layer closeout summary to the user:
     - **Delivered Changes**: Files modified, created, or pruned.
     - **Verification Receipts**: Command outputs proving tests passed.
     - **Decisions Logged**: Summary of any mid-course adjustments from the Decision Log.
   - Explicitly invite user review/audit:
     > *"Plan implementation complete. Please review the changes and receipts above before archive."*

3. **Archive Plan**:
   - Upon user signoff (or if running in autonomous completion mode):
     - Ensure `./ai/archive/` exists (`mkdir -p ./ai/archive`).
     - Flat plan: `mv ./ai/plan.md ./ai/archive/<YYYY-MM-DD>_<plan-slug>.md` (or `mv ./ai/plans/<slug>.md ./ai/archive/<YYYY-MM-DD>_<slug>.md`).
     - Directory board: `mv ./ai/plans/<slug> ./ai/archive/<YYYY-MM-DD>_<slug>`.
   - Confirm the active plan path is cleared so the workspace is ready for the next task.
