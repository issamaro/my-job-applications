# v5-scope-exploration-mode

**Size:** M
**Date:** 2026-01-07
**Est. Files:** 2 (v5-scope.md, v5-feature.md)
**Dependencies:** None

---

## Description

Allow v5-scope to distinguish between solution-oriented and exploration-oriented requests. When user expresses uncertainty ("I don't like X, give alternatives"), the skill should preserve exploratory intent rather than forcing premature specificity.

---

## Scope (IN)

- Add `**Exploration:** true|false` flag to SCOPED_FEATURE template
- v5-scope asks clarifying question when intent is ambiguous: "Are you exploring options or do you know what you want?"
- When exploration=true, Success Criteria can be broader (e.g., "Evaluate 3 approaches")
- v5-feature Analyze phase treats exploration items differently (compare options before planning)

---

## Out of Scope (NOT)

- Separate SCOPED_EXPLORATION template (reuse existing)
- EPIC handling changes (different concern)
- Automated intent detection

---

## Success Criteria

- [ ] v5-scope template includes `**Exploration:** true|false` field
- [ ] v5-scope asks clarifying question when user uses phrases like "alternatives", "options", "explore", "not sure"
- [ ] When exploration=true, v5-feature Analyze phase outputs comparison of approaches before planning
- [ ] Documentation updated explaining when to use exploration mode

---

## Notes

- Discovered during folder-structure-reorganization when user wanted to explore options but got a specific solution
- Flag approach is minimally invasive - doesn't require new backlog item types
- Future: Could add "User expresses uncertainty" to Size Indicators
