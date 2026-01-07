# Note: Backlog Refinement Creates Stale/Overlapping Features

**Date:** 2026-01-06
**Category:** LEARNING
**During:** /v4-scope (merging sort-everything-out.md + skill-environment-awareness.md)

---

## What Happened

During scoping, discovered that `backlog/refined/skill-environment-awareness.md` contained **factually incorrect information**. It stated:

> "Actual project state: Uses `pip`, not `uv`"

But the project had already been migrated to `uv` via `project-tooling-standardization` feature (completed 2026-01-06). The refined feature was outdated the moment it was created because a related feature was implemented first.

## Context

- **File(s):** `backlog/refined/skill-environment-awareness.md`, `backlog/done/project-tooling-standardization.md`
- **Expected:** Refined features contain accurate, current information
- **Actual:** Refined feature contained stale context from before a dependency was implemented

---

## Root Cause Analysis

### 1. Overlapping Features Without Dependency Tracking

Two features in the backlog addressed related concerns:
- `project-tooling-standardization` - Migrate to pyproject.toml + uv
- `skill-environment-awareness` - Make skills detect pip vs uv

When `project-tooling-standardization` was implemented, it invalidated assumptions in `skill-environment-awareness`, but there was no mechanism to flag this.

### 2. Point-in-Time Context Baked Into Refined Features

The SCOPED_FEATURE format captures "Context (Current State)" at refinement time. This becomes stale if:
- Related features are implemented between refinement and execution
- The codebase evolves
- Dependencies change

### 3. No Verification Step Before /v4-feature

`/v4-scope` outputs to `refined/` and assumes the file stays accurate until `/v4-feature` picks it up. No re-verification happens.

---

## Additional Analysis Gaps Discovered

| Gap | Description |
|-----|-------------|
| **v4-* skills not audited** | Original refined feature didn't check what v4-* skills actually say - just assumed |
| **uv pip vs uv sync confusion** | Skills use `uv pip install -r requirements.txt` but modern uv uses `uv sync` with pyproject.toml |
| **No requirements.txt** | Skills reference file that doesn't exist in this project |
| **Assumptions not verified** | Refined feature said "dev.sh uses pip install" - it actually uses `uv sync` |
| **Scope creep potential** | Merged feature now touches 6 global skills, not just project docs |

---

## Resolution

Created new `guidelines-single-source-of-truth.md` that:
1. Actually audited v4-* skills (found outdated `uv pip` patterns)
2. Verified project state (`pyproject.toml` + `uv.lock` present)
3. Documented what each file actually says vs. assumed

Deleted stale files:
- `backlog/refined/skill-environment-awareness.md`
- `backlog/raw/sort-everything-out.md`

---

## Impact

- **Immediate:** Scoping took longer due to re-verification of false assumptions
- **Future:** Consider adding to backlog:
  - "Backlog staleness detection" - flag refined items older than X days
  - "Dependency linking" - track which backlog items affect each other
  - "Re-verification step" - /v4-feature should verify refined context before proceeding
- **Checklist:** Consider adding "Verify refined feature context is current" to /v4-feature

---

## Proposed Process Improvements

1. **Refined features should have dependencies field:**
   ```markdown
   **Dependencies:** project-tooling-standardization (must complete first)
   **Invalidated-by:** Any change to pyproject.toml or tooling
   ```

2. **/v4-feature should re-verify:**
   - Check if "Context (Current State)" still matches reality
   - Flag if dependent features were completed since refinement

3. **Backlog hygiene:**
   - When completing a feature, scan `refined/` for items that may be affected
   - Mark potentially stale items for re-scoping

---

*Captured during guidelines-single-source-of-truth scoping*
