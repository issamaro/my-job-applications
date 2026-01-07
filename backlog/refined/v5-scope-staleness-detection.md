# v5-scope-staleness-detection

**Size:** M
**Date:** 2026-01-07
**Est. Files:** 2 (v5-scope.md, v5-feature.md)
**Dependencies:** None

---

## Description

Prevent refined backlog items from becoming stale when related features are implemented. When a refined item references assumptions about project state (tooling, structure, dependencies), those assumptions may become invalid if other features change that state first.

---

## Scope (IN)

- Add `**Refined:** {DATE}` field to SCOPED_FEATURE template
- Add staleness warning in v5-feature when item is >7 days old
- Add `**Invalidated-by:** {list}` optional field for explicit dependencies
- v5-feature verifies "Context (Current State)" section against actual project state before proceeding

---

## Out of Scope (NOT)

- Automated scanning of refined/ folder after each close
- Complex dependency graph tracking
- Automatic invalidation notifications

---

## Success Criteria

- [ ] v5-scope template includes `**Refined:** {DATE}` field
- [ ] v5-feature checks age and warns if >7 days since refinement
- [ ] v5-feature verifies critical assumptions in Context section before analysis
- [ ] Optional `**Invalidated-by:**` field documented in template

---

## Notes

- Discovered when `skill-environment-awareness.md` claimed "project uses pip" but uv migration had already occurred
- Balance between automation and manual review - start with manual, add automation later if needed
- Age warning is heuristic, not hard blocker
