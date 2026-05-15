# CHANGE_LOG — topbar-shell

| Attribute | Value |
|-----------|-------|
| feature | topbar-shell |
| date | 2026-05-11 |
| commit_base | ffdc989 (refactor(styles): convert color tokens to oklch color space) |
| total_files | 7 |
| total_additions | +422 |
| total_deletions | −69 |

---

## Files by category

### Frontend (5 files)

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| src/components/Topbar.svelte | A | 172 | — |
| src/App.svelte | M | 20 | 20 |
| src/styles/global.css | M | 3 | 1 |
| src/components/TabNav.svelte | D | — | 56 |

### Tests (1 file)

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| tests/test_topbar_shell.py | A | 416 | — |

### Config (1 file)

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| PROJECT_PHASE.md | M | 11 | 9 |

### Other (1 file)

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| workbench/* | A | — | — |

---

## Scope drift

### Files in plan AND changed

- `src/components/Topbar.svelte` — 172 lines (within plan spec ~140 + scoped styles)
- `src/App.svelte` — Lean-code renames: `handleTabChange` → `updateActiveTab`, `handleSwitchTab` → `updateTabFromEvent`; Topbar mounted outside `.container`
- `src/styles/global.css` — body padding 0; `.container` padding var(--spacing-section)
- `tests/test_design_tokens.py` — oklch literals replacing rgb literals (pre-existing red fix per plan §3.4)
- `src/components/TabNav.svelte` — deleted
- `tests/test_topbar_shell.py` — 416 lines, 11 tests (comprehensive playwright smoke; plan spec 5 tests at §8, expanded with 6 additional invariant checks)

### Files changed but NOT in plan

- `PROJECT_PHASE.md` — phase metadata bump (4-5 lines). Not in IMPL_PLAN spec. Low-risk config artifact.
- `workbench/*` — planning + build artifacts (planning doc, inspector payloads, test logs). Not part of source delivery. Low-risk workbench record-keeping.

**Unplanned files by count:** 2 (PROJECT_PHASE.md, workbench/). **Total planned files touched:** 6. **Drift ratio:** 2 ÷ 8 = 25%.

**Drift assessment:** Both unplanned files are **metadata and artifacts only** — no changes to production source code outside the plan. PROJECT_PHASE.md is a phase-tracking file (config, not source). workbench/ is the feature's workbench folder (by project convention, not delivered). Neither touches sensitive areas (auth, db, API contract, public types). **CLEAN**.

---

## Sensitive-area changes

None. Changes are purely structural (Topbar component, layout reflow, test expansion):

- No auth, security config, db migrations, or public API surface changes.
- Function renames in App.svelte are internal (lean-code compliance, no contract change).
- Body → container padding reflow is visual only; `.container` still renders centered 800px max-width below Topbar.
- Test fixes (design-tokens oklch assertions) are baseline correction, not new assertions.

---

## Suggested commit subject

```
feat: add editorial topbar shell and retire legacy tab nav
```

(Combines creation of Topbar + deletion of TabNav + structural changes to App.svelte and global.css.)
