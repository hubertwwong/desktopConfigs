---
name: plan-audit
description: >-
  Use this skill to audit, review, and stress-test an existing implementation plan in ./ai/plan.md,
  ./ai/plans/<slug>.md, or ./ai/plans/<slug>/. Checks for over-engineering, missing test commands, No-Go adherence, and edge cases.
---

# Plan Audit Skill

Use this skill after creating or modifying a plan (`./ai/plan.md`, `./ai/plans/<slug>.md`, or `./ai/plans/<slug>/`) to catch architectural flaws, scope creep, and testing gaps before execution starts.

---

## Audit Checklist

1. **Complexity & Proportionality**:
   - Is the plan over-engineered? Could it be solved with fewer steps or less abstraction?
   - Does it introduce premature abstractions or speculative features?
   - **Size check**: If a flat plan exceeds 10 steps or ~12KB, recommend swapping to a directory board (`./ai/plans/<slug>/{OVERVIEW.md, todo/, doing/, done/}`).

2. **Guardrails & No-Gos**:
   - Are the No-Gos realistic, clear, and enforceable?
   - Do any planned checklist steps or cards violate the stated No-Gos?

3. **Verification Rigor**:
   - Does every single checklist item or card have a concrete, executable verification command?
   - Are edge cases (empty inputs, missing files, network errors) accounted for?

4. **Clarity of Acceptance**:
   - Can the Acceptance Criteria be tested unambiguously?

---

## Output Report Format

Deliver a concise audit report:

- **Verdict**: `APPROVED` | `APPROVED WITH MINOR EDITS` | `REVISION NEEDED`
- **Assessment**: 1-2 sentences on proportionality and fit.
- **Identified Gaps / Risks**: Specific steps or missing verification commands (if any).
- **Recommended Adjustments**: Concrete edits to update the plan.
