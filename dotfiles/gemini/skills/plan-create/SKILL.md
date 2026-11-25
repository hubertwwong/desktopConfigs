---
name: plan-create
description: >-
  Use this skill to draft and scaffold a minimal, test-driven implementation plan in ./ai/plan.md
  (or ./ai/plans/<slug>/ directory board when >10 steps). Enforces North Stars, No-Gos, and concrete verification tests.
---

# Plan Create Skill

Use this skill when initiating a non-trivial or multi-step task. It produces a clear, minimal plan before any production files are modified.

---

## Mode Selection (Flat vs. Directory Board)

- **Flat Plan (default, `<= 10` steps):** Write `./ai/plan.md` (or `./ai/plans/<slug>.md` when juggling multiple concurrent plans).
- **Directory Board (`> 10` steps, `10+` modules, multi-session epic, or flat plan `> 12KB`):** Swap to `./ai/plans/<slug>/`:
  ```text
  ./ai/plans/<slug>/
    OVERVIEW.md   # North Star, No-Gos, Acceptance Criteria, Decision Log
    todo/         # 01-<step>.md, 02-<step>.md ... (1 self-contained card per step)
    doing/        # active card(s) only
    done/         # completed cards (never re-read on resume)
  ```
  If an existing flat plan grows past 10 steps or ~12KB mid-flight, migrate remaining unchecked steps into `todo/` cards, summarize finished work in `OVERVIEW.md`, and archive/remove the old flat file.

---

## Plan Structure (Standard Flat `./ai/plan.md`)

```markdown
# Plan: <Concise Title>

## 1. North Star & Objective
<1-2 sentences: What is the end state? How do we know it succeeded?>

## 2. Guardrails & No-Gos
- 🚫 **No-Go 1**: <What must NOT be broken, deleted, or altered>
- 🚫 **No-Go 2**: <What complexity or dependency is forbidden>
- 🛡️ **Guardrail**: <Syntax, type, or safety invariants>

## 3. Implementation Checklist

- [ ] **Step 1: <Name>**
  - Target files: `<path>`
  - Action: <Minimal change to make>
  - Verification: `<Exact command or test to verify step>`

- [ ] **Step 2: <Name>**
  - Target files: `<path>`
  - Action: <Minimal change to make>
  - Verification: `<Exact command or test to verify step>`

## 4. Acceptance Criteria
- [ ] <End-to-end outcome 1 verified>
- [ ] <End-to-end outcome 2 verified>

## 5. Decision Log & Changes
- **<YYYY-MM-DD>**: Initial plan created.
```

---

## Directory Board Structure (`./ai/plans/<slug>/`)

- **`OVERVIEW.md`**: Same sections `1. North Star & Objective`, `2. Guardrails & No-Gos`, `4. Acceptance Criteria`, and `5. Decision Log & Changes` (cross-card decisions only; no per-step checklist).
- **Card file (`todo/01-<step>.md`)**:
  ```markdown
  # Step 01: <Name>
  - Target files: `<path>`
  - Action: <Minimal change to make>
  - Sub-steps:
    - [ ] <Sub-step if multi-part>
  - Verification: `<Exact command or test to verify card>`
  ```

---

## Authoring Principles

1. **KISS & Proportionality**: Default to a single flat file (`./ai/plan.md` or `./ai/plans/<slug>.md`). Only swap to a directory board when exceeding 10 steps, 10+ modules, ~12KB, or running a multi-session epic.
2. **Concrete Verification Commands**: Every checklist step or card must define the exact command or test used to verify it. Never write "test manually" or "verify it works".
3. **Workspace Boundaries**: Remind that `./ai/` is for internal work products and must never be committed to git.
