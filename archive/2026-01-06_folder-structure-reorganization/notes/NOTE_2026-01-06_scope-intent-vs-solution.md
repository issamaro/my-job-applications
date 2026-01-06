# Note: /v4-scope Too Solution-Oriented for Exploratory Requests

**Date:** 2026-01-06
**Category:** LEARNING
**During:** /v4-scope (folder-structure-separation-of-concerns)

---

## What Happened

When scoping a raw backlog item where the user expressed uncertainty ("I don't like... give relevant alternatives"), /v4-scope jumped directly to proposing concrete sub-features (Backend Consolidation, Documentation Reorganization, etc.) instead of preserving the exploratory nature of the request.

## Context

- **File(s):** `backlog/raw/folder-structure-separation-of-concerns.md`
- **Expected:** Refined item that preserves user's exploratory intent
- **Actual:** Prescribed specific reorganization strategies before user had context to evaluate them

---

## Resolution

Created refined item that:
1. Preserves original user intent verbatim
2. Flags the item as "intent-first" vs "solution-defined"
3. Adds process note for /v4-feature to treat Analyze phase as exploratory

---

## Impact

- **Immediate:** Refined item now correctly signals need for exploration in Analyze
- **Future:** Yes - /v4-scope skill may need refinement
- **Checklist:** No - this is a skill behavior issue, not a project check

---

## Discussion: /v4-scope Responsibility

### Current Behavior
/v4-scope transforms raw ideas → implementation-ready SCOPED_FEATURE with:
- Specific deliverables
- Success criteria
- Files affected estimates

### Problem
This assumes user knows what they want. For exploratory requests, this:
- Prescribes solutions prematurely
- Forces specificity before analysis
- May bias /v4-feature toward predetermined outcomes

### Possible Approaches

**Option A: Two Item Types**
- `SCOPED_FEATURE` (current) - solution-defined, ready for implementation
- `SCOPED_EXPLORATION` (new) - intent-first, needs analysis before planning

**Option B: Flag on Existing Type**
- Add `exploration_needed: true` flag to SCOPED_FEATURE
- /v4-feature checks flag and adjusts Analyze phase accordingly

**Option C: Minimal Change**
- /v4-scope adds "Process Note" section when intent is unclear
- Current approach, but formalized

### Recommendation

Option B seems balanced:
- Doesn't complicate the backlog structure
- Signals to /v4-feature how to handle the item
- Preserves user intent without over-engineering the process

### Questions for Future

1. Should /v4-scope ask "Are you exploring options or do you know what you want?" upfront?
2. Should Size Indicators include "User expresses uncertainty" as a factor?
3. Is the Analyze phase already designed to handle this, and /v4-scope just needs to not over-specify?

---

*Captured during folder-structure-reorganization scoping*
