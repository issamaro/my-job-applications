feature: topbar-shell
date: 2026-05-11
total_checkboxes: 33
derived_from: IMPL_PLAN_2026-05-11_topbar-shell.md, topbar-shell.md (refined backlog)

---

# CHECKLIST — topbar-shell

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = 3.13 (verify: `cat .python-version`)  → source: IMPL_PLAN §8 "playwright smoke (mirrors the shape of test_design_tokens.py)"; pyproject.toml requires-python = ">=3.13"
- [ ] Runtime version pinned: `package.json` devDependencies `svelte ^5.0.0` present (verify: `cat package.json`)  → source: IMPL_PLAN §2 "Svelte 5 runes ($props, $state, $effect) are already used throughout src/components/"
- [ ] Virtual environment created and activated  → source: pyproject.toml [tool.uv] default-groups = ["dev"]

---

## Section 1 — Dependencies

No new libraries added this slice. Source: IMPL_PLAN §2 "None. No new dependency is added."

n/a — no library notes; IMPL_PLAN §2 explicitly states no new dependency.

---

## Section 2 — Syntax

No external library patterns to verify. Svelte 5 rune usage is covered in Section 3 (file-by-file checks).

n/a — no library notes; all patterns are Svelte 5 runes already in use.

---

## Section 3 — UX / File-by-file

*UX design is folded inline in IMPL_PLAN §5. Checks below are derived from §3, §4, §5, and §7.*

### 3.1 CREATE — `src/components/Topbar.svelte`

- [ ] File exists at `src/components/Topbar.svelte`  → source: IMPL_PLAN §3.1 "CREATE — src/components/Topbar.svelte"
- [ ] File opens with exactly two lean-code header lines: license line + `// Scope: …` line, no inline comments anywhere in the file  → source: IMPL_PLAN §3.1 "Header follows lean-code rules (two-line file header, no inline comments, no abbreviations)"; CLAUDE.md lean-code header rule
- [ ] Props declared: `activeTab` (`'profile' | 'resume'`) and `onTabChange` (`(tab: string) => void`)  → source: IMPL_PLAN §3.1 Props table
- [ ] `slots` array hard-coded with exactly 6 entries in order: dashboard, pipeline, jobs, profile, tailor, interview — labels match: Dashboard, Pipeline, Saved jobs, Profile, Tailor CV, Interview prep  → source: IMPL_PLAN §3.1 slots table and §4 decision table
- [ ] `activeSlotId` uses `$derived` (one-liner `slots.find(s => s.tab === activeTab)?.id`) — no separate named helper function for this derivation  → source: IMPL_PLAN §3.1 "Derived value — the active slot id"
- [ ] Click handler is an inline arrow `onclick={() => slot.tab && onTabChange(slot.tab)}` — no function named `handleTabChange` or `handleClick` or any `handle*` / `process*` / `manage*` verb  → source: IMPL_PLAN §3.1 "Click handling"; CLAUDE.md forbidden patterns
- [ ] Disabled slots carry `aria-disabled="true"` and `tabindex="-1"`  → source: IMPL_PLAN §3.1 "aria-disabled={slot.tab === null}" and "tabindex={slot.tab === null ? -1 : 0}"
- [ ] Markup structure: `<header class="topbar">` → `<div class="topbar-brand">` → `<nav class="topbar-nav">` → `{#each slots}` → `<div class="topbar-right">` — matches IMPL_PLAN §3.1 markup block  → source: IMPL_PLAN §3.1 "Markup structure"
- [ ] Each slot is a `<button type="button">`, not a `<div>`  → source: IMPL_PLAN §3.1 "Each slot is a <button type="button">, not a <div>"
- [ ] `<nav aria-label="Primary">` wraps the slot list  → source: IMPL_PLAN §5 a11y bullet "<nav aria-label="Primary"> wrapping the slot list"
- [ ] MyCVLogo inline block: italic "my" + roman "CV" + cobalt dot; uses `var(--font-display)` and `var(--accent)`; dot positioned with `transform: translateY(-2px)` — no hardcoded hex  → source: IMPL_PLAN §3.1 "MyCVLogo (inline in the same file)"
- [ ] Topbar height `64px`, padding `0 32px`, `border-bottom: 1px solid var(--rule)`, `background: var(--paper)`, `display: flex; align-items: center; gap: 36px`  → source: IMPL_PLAN §3.1 "Styles" / "visual targets from shell.jsx lines 110–115"
- [ ] Active slot CSS: `color: var(--ink)`, `font-weight: 500`, `border-bottom: 1px solid var(--ink)`, `margin-bottom: -1px`  → source: IMPL_PLAN §3.1 "Slot active state"
- [ ] Disabled slot CSS: `color: var(--ink-4)`, `cursor: not-allowed`, `pointer-events: none`  → source: IMPL_PLAN §3.1 "Slot disabled state"
- [ ] Search pill CSS: `padding: 6px 10px`, `background: var(--paper-2)`, `border: 1px solid var(--rule)`, `border-radius: var(--r-sm)`, `min-width: 200px`; `⌘K` uses `class="num"`  → source: IMPL_PLAN §3.1 "Search pill"
- [ ] User-initials circle CSS: `30×30`, `border-radius: 50%`, `background: var(--ink)`, `color: var(--paper)`, italic Instrument Serif, shows `LM`  → source: IMPL_PLAN §3.1 "User-initials circle"
- [ ] No hardcoded hex color anywhere in the file — all colors via CSS custom property tokens  → source: IMPL_PLAN §3.1 "Token consumers only (no hardcoded hex)"

### 3.2 MODIFY — `src/App.svelte`

- [ ] `import TabNav` replaced with `import Topbar from './components/Topbar.svelte'`  → source: IMPL_PLAN §3.2 change 1
- [ ] `handleTabChange` renamed to `updateActiveTab` — no other rename; function body unchanged  → source: IMPL_PLAN §3.2 change 2 and CLAUDE.md forbidden pattern `handleX`
- [ ] `<Topbar {activeTab} onTabChange={updateActiveTab} />` renders **outside** `.container` (before the opening `<div class="container">`)  → source: IMPL_PLAN §3.2 change 3 and After block
- [ ] Old `<header class="header"><h1>MyCV</h1><TabNav …/></header>` block is gone  → source: IMPL_PLAN §3.2 Before block
- [ ] The two `{#if activeTab === 'profile'}` and `{#if activeTab === 'resume'}` blocks inside `.container` remain unchanged  → source: IMPL_PLAN §3.2 change 4
- [ ] The `$effect` listening for the `switchTab` window event (lines 12–18) is still present and unmodified  → source: IMPL_PLAN §3.2 change 5 and §7 risk 1

### 3.3 MODIFY — `src/styles/global.css`

- [ ] `body` rule: `padding` is now `0` (was `var(--spacing-section)`)  → source: IMPL_PLAN §3.3 change 1
- [ ] `.container` rule: gains `padding: var(--spacing-section)` (max-width and margin unchanged)  → source: IMPL_PLAN §3.3 change 2
- [ ] Legacy `.header` class block is still present in global.css (intentionally kept)  → source: IMPL_PLAN §3.3 "leave it in place this slice"

### 3.4 DELETE — `src/components/TabNav.svelte`

- [ ] `src/components/TabNav.svelte` no longer exists on disk  → source: IMPL_PLAN §3.4 "Delete it"
- [ ] `grep -rn TabNav src/` returns no matches  → source: IMPL_PLAN §3.4 "verified by grep -rn TabNav src/ returning only the two App.svelte references that this slice removes"

---

## Section 4 — Tests

*Derived from IMPL_PLAN §8 (test plan) and §7 (risks).*

- [ ] Test file `tests/test_topbar_shell.py` exists  → source: IMPL_PLAN §8 "New test file: tests/test_topbar_shell.py"
- [ ] `test_topbar_renders_at_top` — Topbar `<header>` is the first child of `<body>`; contains "MyCV" text and all six slot labels  → source: IMPL_PLAN §8 test 1
- [ ] `test_no_legacy_tab_nav` — `document.querySelector('.tab-nav')` returns null; no `<button>Resume Generator</button>` remains  → source: IMPL_PLAN §8 test 2
- [ ] `test_active_slot_treatment` — on load (activeTab='profile'), Profile slot has computed color matching `--ink` and a 1px bottom border; the other five slots do not  → source: IMPL_PLAN §8 test 3
- [ ] `test_disabled_slots_inert` — `aria-disabled="true"` on Dashboard, Pipeline, Saved jobs, Interview prep; clicking one does not change the visible page  → source: IMPL_PLAN §8 test 4
- [ ] `test_click_tailor_routes` — clicking Tailor CV shows Resume Generator; active treatment moves to Tailor CV slot  → source: IMPL_PLAN §8 test 5
- [ ] `tests/test_design_tokens.py` still passes after global.css body-padding flip (regression guard)  → source: IMPL_PLAN §7 risk 3 and §8 "The existing tests/test_design_tokens.py must still pass"
- [ ] New test file `tests/test_topbar_shell.py` opens with two lean-code header lines; no function names using forbidden verbs (`handle*`, `process*`, `manage*`, `get*`, `fetch*`); function names start only with permitted verbs (`check`, `read`, `render`, etc.)  → source: CLAUDE.md lean-code rules; IMPL_PLAN §3.1 header requirement applies to every new file

---

## Section 5 — Accessibility

*Derived from IMPL_PLAN §5 a11y bullets.*

- [ ] `<header>` element used (not `<div class="topbar">`), giving implicit `role="banner"`  → source: IMPL_PLAN §5 a11y "<header role="banner"> (implicit from element semantics)"
- [ ] `<nav aria-label="Primary">` wraps the slot list (verified in Section 3.1 above; re-check in DOM)  → source: IMPL_PLAN §5 a11y "<nav aria-label="Primary"> wrapping the slot list"
- [ ] Keyboard Tab moves focus through the two enabled slots (Profile, Tailor CV) in DOM order; disabled slots are skipped  → source: IMPL_PLAN §5 "Tab moves focus across enabled slots in DOM order (profile, tailor)"
- [ ] Enter and Space on a focused enabled slot fires `onTabChange`  → source: IMPL_PLAN §5 "Enter/Space on a focused slot fires onTabChange"
- [ ] Search pill and user circle have no focus state and no click handler this slice (decorative)  → source: IMPL_PLAN §5 "Search pill & user circle. Decorative this slice — no click handler, no focus state"

---

## Section 6 — Project-specific

n/a — no project-checks.md found at project root, workbench, or .claude/checks.md.
