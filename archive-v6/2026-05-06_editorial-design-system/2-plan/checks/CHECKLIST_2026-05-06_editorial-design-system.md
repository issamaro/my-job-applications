feature: editorial-design-system
date: 2026-05-06
total_checkboxes: 102
derived_from: IMPL_PLAN_2026-05-06_editorial-design-system.md, FEATURE_SPEC_2026-05-06_editorial-design-system.md, UX_DESIGN_2026-05-06_editorial-design-system.md, LIB_NOTES_2026-05-06_playwright-python.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` — verify: `cat .python-version`
  → source: LIB_NOTES "Version compatibility" — `python>=3.13` required
- [ ] Virtual environment created and activated — verify: `uv run python --version` returns `3.13.x`
  → source: LIB_NOTES "Version compatibility"
- [ ] `playwright>=1.40.0` installed and Chromium binary present — verify: `uv run playwright --version`
  → source: LIB_NOTES "Binary guard pattern"; IMPL_PLAN File 4 — pyproject.toml already declares it
- [ ] Chromium binary downloaded — verify: `uv run playwright install chromium` (no-op if already present)
  → source: LIB_NOTES "playwright install … must be run once on any fresh checkout"

---

## Section 1 — Pre-implementation re-verification

Run these three grep checks **before touching any file**. If any result diverges from expected, stop and escalate.

- [ ] Input-class collision check returns exactly 3 matches (title-input, jd-input, file-input) — verify: `grep -rnE 'class="[^"]*\b(input|textarea)\b[^"]*"' src/components/`
  → source: IMPL_PLAN "Pre-implementation re-verification" row 1; FEATURE_SPEC §MH-6
- [ ] Legacy token usage count is 73 — verify: `grep -rnE 'var\(--(spacing|font-size)' src/components/ | wc -l`
  → source: IMPL_PLAN "Pre-implementation re-verification" row 2; FEATURE_SPEC §MH-1
- [ ] CSS import is at `src/main.js` line 1 — verify: `grep -n "import './styles/global.css'" src/main.js`
  → source: IMPL_PLAN "Pre-implementation re-verification" row 3

---

## Section 2 — `public/index.html`

*IMPL_PLAN File 1. One location, three new `<link>` tags.*

- [ ] Preconnect to `fonts.googleapis.com` present — verify: `grep -n 'preconnect.*fonts.googleapis.com' public/index.html`
  → source: IMPL_PLAN File 1 first new `<link>` line; FEATURE_SPEC §MH-2; covers SC-2
- [ ] Preconnect to `fonts.gstatic.com` with `crossorigin` attribute present — verify: `grep -n 'fonts.gstatic.com.*crossorigin\|crossorigin.*fonts.gstatic.com' public/index.html`
  → source: IMPL_PLAN File 1 second new `<link>` line; covers SC-2
- [ ] Google Fonts stylesheet `<link>` contains exact `family=Fraunces` URL substring — verify: `grep -c 'fonts.googleapis.com/css2?family=Fraunces' public/index.html` returns `1`
  → source: IMPL_PLAN File 1 third new `<link>` line; FEATURE_SPEC §MH-2; covers SC-2
- [ ] Google Fonts `<link>` includes all four families: Fraunces, Instrument Serif, Inter Tight, JetBrains Mono — verify: inspect the stylesheet `href` value manually
  → source: IMPL_PLAN File 1 URL (copied verbatim from tokens.css:5); covers SC-2
- [ ] Total `fonts.googleapis.com` matches is exactly 2 (one preconnect, one stylesheet) — verify: `grep -c 'fonts.googleapis.com' public/index.html` returns `2`
  → source: IMPL_PLAN File 1 "Acceptance"; covers SC-2
- [ ] All three new `<link>` tags appear **before** `<link rel="stylesheet" href="/build/bundle.css">` — verify: line numbers from grep above; font links must have lower line numbers than the bundle link
  → source: IMPL_PLAN File 1 "Edit" paragraph (ordering rationale — IR-1); covers SC-5

---

## Section 3 — `src/styles/global.css`

*IMPL_PLAN File 2. Eleven sub-edits, verified top-down.*

### Edit 2.1 — File header

- [ ] Lean-code two-line header present at top of file — verify: `head -2 src/styles/global.css` shows `/* Lean Code — BSD 3-Clause License — Vivian Voss, 2026 */` then `/* Scope: Editorial design tokens, primitives, and legacy layout utilities. */`
  → source: IMPL_PLAN Edit 2.1 "New (lines 1–8)"
- [ ] WARNING block present with exact grep anchor — verify: `grep -F 'WARNING (slice 1' src/styles/global.css` exits 0 with one match
  → source: IMPL_PLAN Edit 2.1 "Acceptance"; FEATURE_SPEC §MH-5; covers Scenario 18

### Edit 2.2 — `:root` token block

- [ ] Paper tokens present: `--paper`, `--paper-2`, `--paper-3` — verify: `grep -F -- '--paper:' src/styles/global.css` and `grep -F -- '--paper-2:' src/styles/global.css` and `grep -F -- '--paper-3:' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2 `:root` block; FEATURE_SPEC §MH-1 "Paper"; covers SC-1
- [ ] Ink tokens present: `--ink`, `--ink-2`, `--ink-3`, `--ink-4` — verify: `grep -E '^\s+--ink(-[234])?: ' src/styles/global.css | wc -l` returns `4`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Ink"; covers SC-1
- [ ] Rule and card tokens present: `--rule`, `--rule-soft`, `--card` — verify: `grep -E '^\s+--rule|^\s+--card' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Rule / Card"; covers SC-1
- [ ] Accent and status tokens present: `--accent`, `--accent-soft`, `--positive`, `--positive-soft`, `--warn`, `--warn-soft` — verify: `grep -E '^\s+--(accent|positive|warn)' src/styles/global.css | wc -l` returns `6`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Accent + status"; covers SC-1
- [ ] Density tokens at `:root` (spacious values): `--d-pad: 36px`, `--d-gap: 28px`, `--d-row: 64px` — verify: `grep -F -- '--d-pad: 36px' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2 "Density — spacious baked in"; FEATURE_SPEC §MH-1; covers SC-1
- [ ] Radius tokens present: `--r-sm: 2px`, `--r-md: 4px`, `--r-lg: 6px` — verify: `grep -E '^\s+--r-(sm|md|lg):' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Radius"; covers SC-1
- [ ] Shadow token present: `--shadow-card` — verify: `grep -F -- '--shadow-card:' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Shadow"; covers SC-1
- [ ] Type stack tokens present: `--font-display`, `--font-serif`, `--font-ui`, `--font-mono` — verify: `grep -E '^\s+--font-(display|serif|ui|mono):' src/styles/global.css | wc -l` returns `4`
  → source: IMPL_PLAN Edit 2.2; FEATURE_SPEC §MH-1 "Type stacks"; covers SC-1
- [ ] Kept legacy non-color tokens present with unchanged values: `--font-size-body: 16px`, `--font-size-heading: 20px`, `--spacing-grid: 16px`, `--spacing-section: 24px`, `--spacing-field: 12px` — verify: `grep -F -- '--spacing-section: 24px' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.2 "Kept legacy non-color tokens"; FEATURE_SPEC §MH-1; covers SC-1
- [ ] Legacy color aliases present: `--color-text: var(--ink)`, `--color-background: var(--paper)`, `--color-border: var(--rule)`, `--color-primary: var(--accent)`, `--color-error: var(--accent)`, `--color-success: var(--positive)` — verify: `grep -c 'var(--color-' src/styles/global.css` is non-zero; inspect each alias manually
  → source: IMPL_PLAN Edit 2.2 "Legacy color aliases"; FEATURE_SPEC §MH-5; covers SC-1, Scenario 3
- [ ] Legacy `*-rgb` variants present with updated values: `--color-text-rgb: 26 24 20`, `--color-primary-rgb: 184 68 42`, `--color-error-rgb: 184 68 42`, `--color-success-rgb: 74 107 58`, `--color-border-rgb: 200 191 177` — verify: `grep -F '184 68 42' src/styles/global.css | wc -l` returns `2`
  → source: IMPL_PLAN Edit 2.2 "Legacy *-rgb variants"; FEATURE_SPEC §MH-5; covers Scenario 3
- [ ] `--font-stack` is **absent** from the file — verify: `grep -F -- '--font-stack' src/styles/global.css` exits 1 (no match)
  → source: IMPL_PLAN Edit 2.2 "Removed entirely"; FEATURE_SPEC §MH-1; covers SC-1
- [ ] No `[data-theme]`, `[data-accent]`, or `[data-density]` selectors in file — verify: `grep -E '\[data-(theme|accent|density)' src/styles/global.css` exits 1
  → source: IMPL_PLAN Edit 2.2 "Acceptance" SC-8; FEATURE_SPEC §MH-7; covers SC-8, Scenario 6

### Edit 2.3 — `body` rule

- [ ] `body` uses `font-family: var(--font-ui)` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'font-family: var(--font-ui)'`
  → source: IMPL_PLAN Edit 2.3 "New body block"; FEATURE_SPEC §MH-3; covers SC-1, Scenario 1
- [ ] `body` uses `background: var(--paper)` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'background: var(--paper)'`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` uses `color: var(--ink)` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'color: var(--ink)'`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` uses `font-size: 14px` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'font-size: 14px'`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` uses `line-height: 1.5` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'line-height: 1.5'`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` uses `font-feature-settings: 'ss01', 'cv11'` — verify: `grep -F "font-feature-settings: 'ss01'" src/styles/global.css`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` uses `-webkit-font-smoothing: antialiased` — verify: `grep -F '-webkit-font-smoothing: antialiased' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.3; covers Scenario 1
- [ ] `body` retains `padding: var(--spacing-section)` — verify: `grep -A 10 '^body {' src/styles/global.css | grep 'padding: var(--spacing-section)'`
  → source: IMPL_PLAN Edit 2.3 "Keep … padding"; FEATURE_SPEC §MH-3 / R-6; covers SC-7

### Edit 2.6 — `.btn` / `.btn-primary` / `.btn-accent` / `.btn-ghost`

- [ ] `.btn` base rule present with `padding: 9px 14px`, `font-size: 13px`, `font-weight: 500`, `border-radius: var(--r-sm)` — verify: `grep -A 15 '^\.btn {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.6 "New block"; FEATURE_SPEC §MH-4; covers SC-1, Scenario 11
- [ ] `.btn-primary` rule present with `background: var(--ink)`, `color: var(--paper)` — verify: `grep -A 4 '^\.btn-primary {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.6; covers Scenario 12
- [ ] `.btn-accent` rule present with `background: var(--accent)`, `color: white` — verify: `grep -A 4 '^\.btn-accent {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.6; covers Scenario 2
- [ ] `.btn-ghost` rule present with `background: transparent`, `border-color: transparent`, `color: var(--ink-2)` — verify: `grep -A 4 '^\.btn-ghost {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.6; covers Scenario 13
- [ ] Legacy `.btn` / `.btn-primary` bodies removed (no duplicate old blue-style rule) — verify: `grep -F '#0066cc' src/styles/global.css` exits 1
  → source: IMPL_PLAN Edit 2.6 "Remove the legacy bodies entirely"; FEATURE_SPEC §MH-6 "Replaced (collision)"

### Edit 2.7 — `.btn-add` kept verbatim

- [ ] `.btn-add` rule present with `padding: 4px 8px; font-size: 14px` unchanged — verify: `grep -A 3 '^\.btn-add {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.7; FEATURE_SPEC §MH-6 "Kept (extension)"; covers SC-7
- [ ] `.btn-add` appears immediately after `.btn-ghost` block — verify: line order in file (`.btn-ghost` last line before `.btn-add`)
  → source: IMPL_PLAN Edit 2.7 "Move it to sit immediately after"
- [ ] `Section.svelte:23` applies both `btn` and `btn-add` classes — verify: `grep -n 'btn-add' src/components/Section.svelte` shows `btn btn-add` together
  → source: IMPL_PLAN Edit 2.7 "Pre-implementation check"; FEATURE_SPEC R-5

### Edit 2.8 — Pill primitives

- [ ] `.pill` base rule present with `font-family: var(--font-mono)`, `font-size: 10px`, `border-radius: 999px`, `text-transform: uppercase`, `letter-spacing: 0.06em` — verify: `grep -A 12 '^\.pill {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.8; FEATURE_SPEC §MH-4; covers SC-1, Scenario 14
- [ ] `.pill-accent` rule present with `color: var(--accent)`, `border-color: var(--accent)`, `background: var(--accent-soft)` — verify: `grep -A 4 '^\.pill-accent {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.8; covers Scenario 15
- [ ] `.pill-positive` rule present — verify: `grep -A 4 '^\.pill-positive {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.8; covers Scenario 15
- [ ] `.pill-warn` rule present — verify: `grep -A 4 '^\.pill-warn {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.8; covers Scenario 15
- [ ] `.pill-solid` rule present with `background: var(--ink)`, `color: var(--paper)` — verify: `grep -A 4 '^\.pill-solid {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.8; covers Scenario 15

### Edit 2.9 — Typography primitives, rules, card

- [ ] `.eyebrow` rule present with `font-family: var(--font-mono)`, `font-size: 10px`, `letter-spacing: 0.12em`, `text-transform: uppercase`, `color: var(--ink-3)`, `font-weight: 500` — verify: `grep -A 7 '^\.eyebrow {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; FEATURE_SPEC §MH-4; covers SC-1, Scenario 4
- [ ] `.display` rule present with `font-family: var(--font-display)`, `letter-spacing: -0.01em`, `line-height: 1.05` — verify: `grep -A 5 '^\.display {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 4
- [ ] `.serif-italic` rule present with `font-family: var(--font-display)`, `font-style: italic` — verify: `grep -A 4 '^\.serif-italic {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 7
- [ ] `.num` rule present with `font-family: var(--font-mono)`, `font-variant-numeric: tabular-nums` — verify: `grep -A 3 '^\.num {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 8
- [ ] `.rule` rule present with `border: 0; border-top: 1px solid var(--rule); margin: 0` — verify: `grep -A 4 '^\.rule {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 9
- [ ] `.rule-soft` rule present with `border-top: 1px solid var(--rule-soft)` — verify: `grep -A 4 '^\.rule-soft {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 9
- [ ] `.card` rule present with `background: var(--card)`, `border: 1px solid var(--rule)`, `border-radius: var(--r-md)` — verify: `grep -A 4 '^\.card {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.9; covers Scenario 10

### Edit 2.10 — Coexistence comment + raw `input, textarea, select`

- [ ] Coexistence comment present immediately before raw selector block — verify: `grep -F 'Note: the rules below' src/styles/global.css` exits 0 with one match
  → source: IMPL_PLAN Edit 2.10 "Acceptance"; FEATURE_SPEC §MH-6 R-2; covers Scenario 19
- [ ] Raw `input, textarea, select { ... }` block body unchanged (padding 8px, font-size var(--font-size-body), etc.) — verify: `grep -A 14 '^input,' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.10 "The body is unchanged"; covers SC-7

### Edit 2.11 — Editorial `.input` / `.textarea` classes

- [ ] `.input, .textarea` rule present with `padding: 10px 12px`, `font-family: var(--font-ui)`, `font-size: 13px`, `color: var(--ink)`, `background: var(--paper)`, `border: 1px solid var(--rule)`, `border-radius: var(--r-sm)`, `outline: none` — verify: `grep -A 10 '^\.input, \.textarea {' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.11; FEATURE_SPEC §MH-4; covers SC-1, Scenario 16
- [ ] `.input:focus, .textarea:focus` rule sets `border-color: var(--ink)` — verify: `grep -F '.input:focus' src/styles/global.css`
  → source: IMPL_PLAN Edit 2.11; covers Scenario 16, Scenario 17
- [ ] `.textarea { resize: vertical; }` rule present — verify: `grep -F 'resize: vertical' src/styles/global.css | grep -F '.textarea'`
  → source: IMPL_PLAN Edit 2.11; covers Scenario 17

---

## Section 4 — `tests/test_design_tokens.py`

- [ ] File exists — verify: `ls tests/test_design_tokens.py`
  → source: IMPL_PLAN File 3 "CREATE"; covers SC-9
- [ ] Lean-code two-line header present: `# Lean Code — BSD 3-Clause License — Vivian Voss, 2026` then `# Scope: Smoke-test the editorial body restyle reaches the served bundle.` — verify: `head -2 tests/test_design_tokens.py`
  → source: IMPL_PLAN File 3 "Test file structure" lines 1–2; CLAUDE.md Lean Code rules
- [ ] `sync_playwright()` used (not async) with `try/finally` for `browser.close()` — verify: inspect file for `with sync_playwright()` and `finally: browser.close()`
  → source: LIB_NOTES "sync_playwright() context manager" and "Closing / cleanup inside with sync_playwright()"; IMPL_PLAN File 3
- [ ] `browser.new_context()` + `context.new_page()` used (not bare `browser.new_page()`) — verify: inspect file
  → source: LIB_NOTES Pattern 4 "new_context() + new_page() vs new_page()"
- [ ] `page.goto(public_url, wait_until="load")` used — verify: inspect file
  → source: LIB_NOTES Pattern 3; IMPL_PLAN File 3
- [ ] `page.evaluate("() => document.fonts.ready")` called after `goto` — verify: inspect file
  → source: LIB_NOTES Pattern 3 "font loading"; IMPL_PLAN File 3 "Open question 2"
- [ ] `getPropertyValue('-webkit-font-smoothing')` used (not `computed.webkitFontSmoothing`) — verify: inspect file
  → source: LIB_NOTES "Open question 1"; IMPL_PLAN File 3 "Open question 1 handled"
- [ ] `webkitFontSmoothing` assertion is gated: `if styles["webkitFontSmoothing"]:` — verify: inspect file
  → source: IMPL_PLAN File 3 "Open question 1 handled — gated on truthy return value"
- [ ] Seven body assertions present: `backgroundColor`, `color`, `fontFamily.startswith`, `fontSize`, `lineHeight`, `fontFeatureSettings` contains `ss01`, `fontFeatureSettings` contains `cv11` — verify: inspect file
  → source: IMPL_PLAN File 3 assertions block; FEATURE_SPEC Scenario 1; covers SC-9, Scenario 20
- [ ] `public_url` fixture skips when `public/build/bundle.css` is missing — verify: inspect fixture body for `pytest.skip`
  → source: IMPL_PLAN File 3 "Playwright binary guard"
- [ ] Test passes: `uv run pytest tests/test_design_tokens.py` exits 0 — verify: run it
  → source: IMPL_PLAN File 3 "Acceptance"; FEATURE_SPEC SC-9, Scenario 20

---

## Section 5 — Cross-cutting verifications

- [ ] Build succeeds: `bun run build` exits 0
  → source: IMPL_PLAN "Execution order" step 4; covers SC-3
- [ ] Editorial token reached bundle: `grep -F -- '--paper: #f4f1ec' public/build/bundle.css` returns exactly one match
  → source: IMPL_PLAN "Execution order" step 4; FEATURE_SPEC SC-3; covers SC-3
- [ ] No `[data-*]` attribute selectors leaked: `grep -E '\[data-(theme|accent|density)' src/styles/global.css` exits 1
  → source: IMPL_PLAN "Test plan" row 6; FEATURE_SPEC SC-8; covers SC-8, Scenario 6
- [ ] Full test suite still passes: `uv run pytest` exits 0 (no regressions)
  → source: IMPL_PLAN "Execution order" step 7; FEATURE_SPEC SC-4; covers SC-4
- [ ] `bun run build` emits no CSS parse warnings to stderr — verify: inspect build output
  → source: UX_DESIGN "Error" state — "bun run build exits 0 with no parse warnings in stderr"

---

## Section 6 — Manual / inspect phase

*Run after build and automated tests pass. Open the app at `http://localhost:8000/` via `uv run uvicorn main:app --reload`.*

### Intended visible deltas — confirm these are present (not regressions)

- [ ] Page background is paper `#f4f1ec`, not white — DevTools: Computed → background-color = `rgb(244, 241, 236)`
  → source: UX_DESIGN "Intended visible deltas" #1; covers SC-5, SC-7
- [ ] Body text color is ink `#1a1814`, not `#1a1a1a` — DevTools: Computed → color = `rgb(26, 24, 20)`
  → source: UX_DESIGN "Intended visible deltas" #2; covers SC-5
- [ ] Body font is Inter Tight (visible in DevTools → Computed → font-family starts with `"Inter Tight"`)
  → source: UX_DESIGN "Intended visible deltas" #3; covers SC-5
- [ ] All `.btn-primary` consumers (ResumeView download, WorkExperience save ×2, Education save ×2, Skills add, ResumeGenerator buttons) render ink-filled (`#1a1814`), not blue
  → source: UX_DESIGN "Intended visible deltas" #4; covers SC-7
- [ ] Form input focus rings are terracotta (`#b8442a`), not blue — click any `<input>` in profile editor
  → source: UX_DESIGN "Intended visible deltas" #5; IMPL_PLAN Edit 2.10; covers SC-7

### Expected color drifts (document, do not fail)

- [ ] `.status` and `.saved-indicator` render editorial green `#4a6b3a` (darker than legacy `#008800`) — note in inspector log as expected
  → source: IMPL_PLAN Edit 2.5 "Inspector phase" note; IMPL_PLAN "Inspector phase preparation"
- [ ] `.delete-link` and `.error-message` render terracotta `#b8442a` (same as primary CTA) — confirm WARNING comment documents this; check discoverability in profile editor "Are you sure?" flow
  → source: IMPL_PLAN "Inspector phase preparation"; FEATURE_SPEC §MH-5 "Known compromise"
- [ ] `.form-error` background resolves to light terracotta tint (rgb(184,68,42)/0.05), not light red — verify in a form with a validation error
  → source: IMPL_PLAN "Inspector phase preparation"; FEATURE_SPEC Scenario 3

### Per-primitive computed-style checks (DevTools or scratch page injection)

- [ ] `.eyebrow` — font-family starts with `"JetBrains Mono"`, text-transform=uppercase, letter-spacing=0.12em, color=`rgb(107, 99, 88)`
  → source: UX_DESIGN "Typography primitives" table; FEATURE_SPEC Scenario 4; covers SC-6
- [ ] `.display` — font-family starts with `"Instrument Serif"`, letter-spacing=-0.01em
  → source: UX_DESIGN "Typography primitives" table; FEATURE_SPEC Scenario 4; covers SC-6
- [ ] `.serif-italic` — font-family starts with `"Instrument Serif"`, font-style=italic, font-weight=400
  → source: UX_DESIGN "Typography primitives" table; FEATURE_SPEC Scenario 7; covers SC-6
- [ ] `.num` — font-family starts with `"JetBrains Mono"`, font-variant-numeric contains tabular-nums
  → source: UX_DESIGN "Typography primitives" table; FEATURE_SPEC Scenario 8; covers SC-6
- [ ] `.rule` — border-top 1px solid `rgb(200, 191, 177)`, margin 0
  → source: UX_DESIGN "Rules / dividers" table; FEATURE_SPEC Scenario 9; covers SC-6
- [ ] `.rule-soft` — border-top 1px solid `rgb(221, 213, 199)`
  → source: UX_DESIGN "Rules / dividers" table; FEATURE_SPEC Scenario 9; covers SC-6
- [ ] `.card` — background `rgb(251, 250, 246)`, border `1px solid rgb(200, 191, 177)`, border-radius 4px
  → source: UX_DESIGN "Card" table; FEATURE_SPEC Scenario 10; covers SC-6
- [ ] `.btn` hover — background shifts to `--paper-2` and border to `--ink-3` within ~150ms
  → source: UX_DESIGN "Buttons" table hover column; covers SC-6
- [ ] `.pill` — border-radius 999px, font-size 10px, text-transform uppercase, letter-spacing 0.06em, color `rgb(107, 99, 88)`
  → source: UX_DESIGN "Pills" table; FEATURE_SPEC Scenario 14; covers SC-6
- [ ] `.pill-accent`, `.pill-positive`, `.pill-warn`, `.pill-solid` — each color/bg/border triple matches FEATURE_SPEC Scenario 15 table
  → source: UX_DESIGN "Pills" table; FEATURE_SPEC Scenario 15; covers SC-6
- [ ] `.input` — border swaps to `--ink` on focus, no browser outline visible
  → source: UX_DESIGN "Inputs" table; FEATURE_SPEC Scenario 16; covers SC-6
- [ ] `.textarea` — same as `.input` plus resize: vertical
  → source: UX_DESIGN "Inputs" table; FEATURE_SPEC Scenario 17; covers SC-6

### DevTools network check

- [ ] `fonts.googleapis.com` returns 200 for the CSS stylesheet — DevTools Network filter: `googleapis`
  → source: UX_DESIGN "DevTools" verification checklist; FEATURE_SPEC Scenario 5; covers SC-5
- [ ] `fonts.gstatic.com` returns 200 for each font file: Instrument Serif, Fraunces, Inter Tight, JetBrains Mono — DevTools Network filter: `gstatic`
  → source: UX_DESIGN "DevTools" verification checklist; FEATURE_SPEC Scenario 5; covers SC-5
- [ ] No console errors related to fonts or CSS
  → source: UX_DESIGN "For the existing screens" checklist last bullet; covers SC-5

### Layout regression check

- [ ] Existing forms still align, accept input, save, and validate — no layout collapse from body restyle
  → source: UX_DESIGN "For the existing screens" checklist; covers SC-7
- [ ] Font fallbacks legible when `fonts.googleapis.com` is blocked — disable network in DevTools, reload
  → source: UX_DESIGN "Loading (network)" state; covers SC-5 / SC-7

---

## Section 7 — Project-specific

n/a — no project-checks.md found at project root.

Authoritative check set used instead: FEATURE_SPEC Success Criteria SC-1 through SC-9 and BDD Scenarios 1 through 20 (all referenced via `→ source:` annotations throughout this document).
