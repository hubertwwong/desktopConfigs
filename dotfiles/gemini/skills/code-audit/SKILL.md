---
name: code-audit
description: >-
  Use this skill to audit, review, or critique code, git diffs, or PRs.
  Evaluates modularity, shallow wrappers, KISS, and Core 3 tests separately
  from Spec fit.
---

# Code Audit Skill

Performs a two-axis, risk-tiered review focused on structural maintainability and spec fit.

## Axis 1: Design & Quality Review
1. **Modularity & Shallow Wrappers**: Check separation of concerns (`I/O`, domain logic, `CLI`) and flag shallow pass-through wrappers whose interface rivals their body.
2. **Testing Pragmatism (Core 3)**: Verify observable behavior at public seams across happy path, boundaries, and failure modes with independent expected values (flag mock overkill).
3. **KISS & Resource Safety**: Flag speculative abstractions, implicit failures, unclosed handles (`with`/`defer`), and fragile Bash parsing.
4. **Risk-Tiered Scrutiny**: Focus deepest review on hooks, auth, state/schema changes, and public interfaces; run the project's test suite before issuing `CLEAN`.

## Axis 2: Spec & Scope Fit *(when an active plan or spec exists)*
- Confirm every requirement from `./ai/plan.md` or the user request is met without unrequested scope creep.

## Output Audit Report
Report **Standards** and (when a spec exists) **Spec** separately without merging verdicts:
```markdown
# Code Audit Summary
- **Standards Verdict**: `CLEAN` | `APPROVED WITH SUGGESTIONS` | `CHANGES REQUESTED`
- **Spec Verdict** *(if plan/spec exists)*: `COMPLETE` | `GAPS FOUND`
## Standards Findings (Modularity, Core 3, KISS, Safety)
## Spec Findings *(if applicable)*
## Concrete Recommendations & Diffs
```
