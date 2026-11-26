---
name: plan-audit
description: >-
  Use this skill to audit and stress-test an implementation plan in ./ai/plan.md,
  ./ai/plans/<slug>.md, or ./ai/plans/<slug>/ before execution. Checks strategy
  alignment, seams, proportionality, and verification rigor.
---

# Plan Audit Skill

Reviews a drafted plan to catch silent assumptions, weak seams, scope creep, and testing gaps before implementation begins.

## Audit Checklist

1. **Strategy & Open Decisions**:
   - Are design choices settled with the user rather than silently assumed?
   - Does the plan solve the stated North Star directly without speculative abstractions?
2. **Seams & Vertical Slicing**:
   - Do steps land at clean public seams as verifiable **tracer bullets** (or **expand–contract** for wide refactors)?
   - Is each step small enough to verify independently?
3. **Proportionality & Mode Fit**:
   - Flat plan stays `<= 10` steps and `<= 12KB`; larger epics use `./ai/plans/<slug>/{OVERVIEW.md,todo/,doing/,done/}`.
4. **Guardrails & Verification Rigor**:
   - Every checklist step and Acceptance Criterion ends on a concrete, executable verification command covering happy path, boundaries, and failure modes.
   - No step conflicts with the stated No-Gos or commits `./ai/`.

## Output Report Format
- **Verdict**: `APPROVED` | `APPROVED WITH MINOR EDITS` | `REVISION NEEDED`
- **Assessment**: 1–2 sentences on strategic fit and proportionality.
- **Identified Gaps / Risks**: Specific unsettled decisions, weak seams, or missing checks.
- **Recommended Adjustments**: Concrete edits to update the plan before execution.
