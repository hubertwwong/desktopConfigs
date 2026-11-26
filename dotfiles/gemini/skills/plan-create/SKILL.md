---
name: plan-create
description: >-
  Use this skill when initiating a non-trivial or multi-step task. Aligns upfront
  strategy, seams, and vertical slices before drafting ./ai/plan.md (or
  ./ai/plans/<slug>/ when exceeding 10 steps).
---

# Plan Create Skill

Produces a minimal, strategy-aligned plan before production files are touched.

## 1. Upfront Strategy & Alignment (Before Drafting Steps)
1. **Fact-Find First**: Inspect existing code, configs, and tests yourself before asking questions.
2. **Resolve Unsettled Decisions**: Present remaining design branches to the user in focused rounds (`ask_question`) with a recommended default—leave zero silent assumptions.
3. **Pick the Test Seam & Slice Vertically**:
   - Anchor verification at the cleanest public **seam** (prefer existing interfaces).
   - Sequence work as **tracer bullets** (narrow, verifiable end-to-end slices) rather than horizontal layers.

## 2. Mode Selection (Flat vs. Directory Board)
- **Flat Plan (default, `<= 10` steps / `<= 12KB`)**: Write `./ai/plan.md` (or `./ai/plans/<slug>.md`).
- **Directory Board (`> 10` steps, `10+` modules, or `> 12KB`)**: Use `./ai/plans/<slug>/`:
  - `OVERVIEW.md`: Sections 1, 2, 4, and 5 below.
  - `todo/`, `doing/`, `done/`: Self-contained cards (`01-<step>.md`; skip `done/` on resume):
    ```markdown
    # Step 01: <Name>
    - Target files: `<path>`
    - Action: <Minimal change at target seam>
    - Verification: `<Exact executable command or test>`
    ```

## 3. Plan Template (`./ai/plan.md`)
```markdown
# Plan: <Concise Title>

## 1. North Star & Objective
<1-2 sentences: target end state and how success is verified.>

## 2. Guardrails & No-Gos
- 🚫 **No-Go**: <Hard boundary that must stay intact>
- 🛡️ **Guardrail**: <Type, size, or safety invariant>

## 3. Implementation Checklist
- [ ] **Step 1: <Vertical Slice Name>**
  - Target files: `<path>`
  - Action: <Minimal change at target seam>
  - Verification: `<Exact executable command or test>`

## 4. Acceptance Criteria
- [ ] <Checkable end-to-end outcome>

## 5. Decision Log & Changes
- **<YYYY-MM-DD>**: Initial plan created.
```

## 4. Authoring Standards
- **Executable Verification Only**: Every step and criterion ends on a concrete command or assertion.
- **KISS & Scope Discipline**: Keep `./ai/` internal (uncommitted); target `<= 8` steps whenever practical and verify non-trivial plans with `plan-audit`.
