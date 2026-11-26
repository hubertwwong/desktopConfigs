---
name: code-create
description: >-
  Use this skill when asked to write, implement, refactor, or test code.
  Enforces modular design, KISS/YAGNI, and red-first Core 3 tests at public seams.
---

# Code Create Skill

Keeps authored code modular, debuggable, and tested without over-engineering. *(Mechanical line limits and silent-except checks are enforced by `code_guard`.)*

## 1. Modularity & Simplicity (Anti-Monstrosity)
- **Split by Concern**: Separate parsing/I-O, core domain logic, and CLI/presentation into focused modules and `< 30`-line functions.
- **Python/Go Over Bash**: Keep Bash to `< 15` lines of CLI dispatch; use Python or Go for data parsing, loops, math, or logic needing tests.
- **KISS & YAGNI**: Write the direct solution first; extract shared abstractions once a third distinct caller emerges.
- **Fail Fast & Loud**: Validate preconditions at entrypoints, propagate errors with context, and preserve unrelated comments/docstrings.
- **Scratch Discipline**: Keep throwaway scripts in `./ai/scratch/` (uncommitted).

## 2. Red-First Core 3 Testing (At Public Seams)
Work in vertical slices (`failing check → minimal code → green → repeat`):
1. **Red Before Green**: For bugs or new behavior, run a failing test/repro at the public seam before theorizing or editing implementation code.
2. **Independent Ground Truth**: Assert against known-good literals or specs, avoiding assertions that recompute implementation logic.
3. **Cover The Core 3**:
   - **Happy Path**: Valid input produces expected output.
   - **Boundary**: Empty (`[]`, `""`), `None`/`nil`, or zero/negative inputs.
   - **Expected Failure**: Invalid inputs raise or return explicit errors.
4. **Minimal Mocking**: Use real stdlib structures; stub only external network APIs, slow DBs, or external processes.
