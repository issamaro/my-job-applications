# CHANGE_LOG — editorial-design-system

**Feature:** editorial-design-system  
**Date:** 2026-05-06  
**Commit base:** HEAD  
**Total files:** 3  
**Total additions:** +221  
**Total deletions:** -46  

---

## Changes by category

### Frontend (2 files)

| File | Change | +Lines | -Lines |
|------|--------|--------|--------|
| public/index.html | M | 3 | 0 |
| src/styles/global.css | M | 218 | 46 |

### Tests (1 file)

| File | Change | +Lines | -Lines |
|------|--------|--------|--------|
| tests/test_design_tokens.py | A | 0 | 0 |

---

## Scope drift

None. All three changed files appear in the IMPL_PLAN. All planned files are accounted for.

---

## Sensitive-area changes

**Design tokens (core):** src/styles/global.css

- Editorial palette introduced (paper, ink, accent, positive, warn scales)
- Typography stacks ported (display, serif, ui, mono)
- Legacy color aliases recomputed to editorial tokens
- New primitives added (.eyebrow, .display, .serif-italic, .num, .rule, .card, .pill, .input, .textarea)
- WARNING block added documenting --color-error aliased to --accent until slice 2+

**No database, auth, or public API surface changes.** Font load order change in HTML is intentional per plan (Google Fonts preconnect before bundle CSS).

---

## Suggested commit subject

```
feat(styles): port editorial tokens and primitives (slice 1/9)
```

Rationale: introduces editorial design-token layer and component primitives as foundation for the 9-slice editorial redesign initiative. Legacy aliases preserve backward compatibility; no component code changes required.
