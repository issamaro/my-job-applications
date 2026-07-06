# CHANGE_LOG — screen-frame-ownership — 2026-07-06

**feature:** screen-frame-ownership  
**date:** 2026-07-06  
**commit_base:** HEAD  
**total_files:** 6 (5 modified, 1 created)  
**total_additions:** +168  
**total_deletions:** −81

---

## Files by category

### Frontend

| File | Change | +lines | −lines |
|------|--------|--------|--------|
| src/App.svelte | M | 5 | 7 |
| src/components/ResumeGenerator.svelte | M | 65 | 58 |
| src/styles/global.css | M | 0 | 11 |

### Tests

| File | Change | +lines | −lines |
|------|--------|--------|--------|
| tests/test_design_tokens.py | M | 19 | 0 |
| tests/test_topbar_shell.py | M | 6 | 5 |
| tests/test_generator_frame.py | A | 73 | 0 |

---

## Scope drift

none

---

## Sensitive-area changes

none

---

## Out-of-feature changes (do not commit with this feature)

These files were modified before or outside this feature's scope:

| File | Change | +lines | −lines | Reason |
|------|--------|--------|--------|--------|
| .mcp.json | M | 4 | 0 | Pre-existing modification (Atlassian MCP server config) |

Untracked directories (pre-existing):
- `.claude/skills/` — pre-existing, unrelated to feature
- `workbench/` — feature artifacts (plan, checklist, reviews, test results, screenshots, notes) — archived by git-closer

---

## Suggested commit subject

```
refactor: move layout container from app shell to screens
```

---

## Summary of changes

**Screen-level framing:** Removed the app shell's `.container` wrapper and rules; each screen now self-frames:
- **App.svelte:** Deleted wrapper div; `{#if}` chain moved to direct children of Topbar.
- **global.css:** Deleted `.container` and `.container-wide` rules (padding/centering rules moved to screen level).
- **ResumeGenerator.svelte:** Added `.generator-frame` div (800px, centered, temporary) wrapping the input/loading branches; preview branch unframed and full-bleed.

**Tests:** Added static guard to prevent container reintroduction; added geometry smoke-test for generator frame; updated topbar test to target `.editor-main` (ProfileEditor's main element) instead of deleted `.container`.

**Design ledger:** Change is marked in `design-bundle/SLICE_INDEX.md` (gitignored) for slice 6's restyle to consume.
