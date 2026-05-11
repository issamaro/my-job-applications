# IMPL_PLAN — editorial-design-system

**Date:** 2026-05-06
**Slug:** editorial-design-system
**Ceremony level:** M
**Slice:** 1 of 9 (foundation) in the editorial redesign initiative

## Inputs honoured

- `backlog/refined/editorial-design-system.md`
- `workbench-v6/1-analyze/spec/FEATURE_SPEC_2026-05-06_editorial-design-system.md`
- `workbench-v6/1-analyze/ux/UX_DESIGN_2026-05-06_editorial-design-system.md`
- `workbench-v6/1-analyze/spec/ANALYSIS_VERIFIED_2026-05-06_editorial-design-system.md` (status: VERIFIED)
- `workbench-v6/2-plan/research/LIB_NOTES_2026-05-06_playwright-python.md` (status: PARTIAL — two open questions baked into the plan below)
- `design-bundle/project/tokens.css` (rule bodies copied verbatim from here)

## Pre-implementation re-verification (run at start of build phase)

The FEATURE_SPEC pinned three grep assertions made during analyze. Re-run these before the first edit. If any return a different result than below, **stop and escalate via `note-capturer`** before touching `global.css`.

| Command | Expected | Why |
|---|---|---|
| `grep -rnE 'class="[^"]*\b(input\|textarea)\b[^"]*"' src/components/` | exactly three matches — `SavedJobItem.svelte:125 title-input`, `JobInput.svelte:18 jd-input`, `ImportModal.svelte:263 file-input` (all unrelated tokens; no bare `.input`/`.textarea`) | Spec §MH-6 — collision-safety claim |
| `grep -rnE 'var\(--(spacing\|font-size)' src/components/ \| wc -l` | `73` | Spec §MH-1 — kept-legacy-tokens justification |
| `grep -n "import './styles/global.css'" src/main.js` | one match at line 1 | Confirms the CSS edits will reach `public/build/bundle.css` via rollup |

## File-by-file plan

### File 1 — `public/index.html` (MODIFY, 1 location)

**Current:** 13 lines; `<head>` contains `<meta charset>`, `<meta viewport>`, `<title>`, and the bundle stylesheet `<link>`.

**Edit:** insert three `<link>` elements inside `<head>`, immediately **after** the `<title>` tag and **before** the existing `<link rel="stylesheet" href="/build/bundle.css">`. Placing Google Fonts before the bundle CSS ensures the fonts are queued during HTML parse, not blocked behind the bundle.

The three new lines (exact content, no copyright header — `index.html` has none today and lean-code's two-line comment header rule does not apply to HTML files in this project):

```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700;9..144,800&family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
```

The URL is copied verbatim from `design-bundle/project/tokens.css:5` minus the `@import url(...)` wrapper. SC-2 verifies the exact URL substring `fonts.googleapis.com/css2?family=Fraunces`.

**Acceptance:** `grep -n 'fonts.googleapis.com' public/index.html` returns 2 matches (one preconnect, one stylesheet).

---

### File 2 — `src/styles/global.css` (MODIFY, multi-region rewrite)

This is the load-bearing edit. The file is 350 lines today; the post-edit file will be roughly 430–470 lines (token block grows by ~30 lines; primitives add ~120 lines; legacy bodies for `.btn`/`.btn-primary`/`.input`/`.textarea` removed save ~30 lines).

**Edits proceed top-down so later edits don't shift line numbers for earlier ones.**

#### Edit 2.1 — File header (line 1)

Replace the existing one-line header with the lean-code two-line header **plus** the five-line `WARNING (slice 1` comment block from FEATURE_SPEC §MH-5. The CSS comment syntax is `/* ... */` (not `//`).

**Old (line 1):**
```css
/* global.css - CSS Custom Properties + reset + layout + utilities + shared styles */
```

**New (lines 1–8):**
```css
/* Lean Code — BSD 3-Clause License — Vivian Voss, 2026 */
/* Scope: Editorial design tokens, primitives, and legacy layout utilities. */

/* WARNING (slice 1 / editorial-design-system, 2026-05-06):
   --color-error currently resolves to --accent (terracotta).
   The editorial palette has no dedicated error token. Do NOT
   introduce new error semantics on this alias — replace it with
   a slice-specific token before adding any new validation UI. */
```

The lean-code header replaces the legacy header; the WARNING block sits immediately after, satisfying FEATURE_SPEC §MH-5's "immediately after the existing single-line file-header comment and before any `:root` rule".

**Acceptance:** `grep -F 'WARNING (slice 1' src/styles/global.css` exits 0 with one matching line. Covers Scenario 18.

**Lean-code note:** the existing global.css file has only the legacy single-line comment — no lean-code header. This edit retrofits the lean-code header onto the file as part of the slice's normal scope (we're rewriting the token block anyway). No other CSS file in `src/styles/` is restructured by this slice.

#### Edit 2.2 — `:root` block (currently lines 6–31)

Replace the entire `:root { ... }` block with the editorial tokens + kept legacy values + legacy color aliases. Rule order inside `:root` matters only for `*-rgb` aliasing readability, not behavior. Group order: editorial type stacks → editorial palette → density → radius → shadow → kept legacy non-color tokens → legacy color aliases (recomputed on top of editorial).

**Reference body (rule values copied from `design-bundle/project/tokens.css:7–43`; density values **overridden** to the spacious set per FEATURE_SPEC §MH-1; aliases per §MH-5):**

```css
:root {
  /* Editorial type stacks */
  --font-display: 'Instrument Serif', 'Fraunces', Georgia, serif;
  --font-serif: 'Fraunces', Georgia, serif;
  --font-ui: 'Inter Tight', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  /* Editorial palette — paper */
  --paper: #f4f1ec;
  --paper-2: #ece7df;
  --paper-3: #e0d9cd;

  /* Editorial palette — ink */
  --ink: #1a1814;
  --ink-2: #3a342c;
  --ink-3: #6b6358;
  --ink-4: #9c9387;

  /* Editorial palette — structure */
  --rule: #c8bfb1;
  --rule-soft: #ddd5c7;
  --card: #fbfaf6;

  /* Editorial palette — accent + status */
  --accent: #b8442a;
  --accent-soft: #e9c8bd;
  --positive: #4a6b3a;
  --positive-soft: #d6dec9;
  --warn: #a07024;
  --warn-soft: #ead8b6;

  /* Density — spacious baked in */
  --d-pad: 36px;
  --d-gap: 28px;
  --d-row: 64px;

  /* Radius */
  --r-sm: 2px;
  --r-md: 4px;
  --r-lg: 6px;

  /* Shadow — reserved for slices 7 & 8 */
  --shadow-card: 0 1px 0 rgba(26,24,20,0.04), 0 12px 32px -16px rgba(26,24,20,0.18);

  /* Kept legacy non-color tokens — referenced by src/components/ */
  --font-size-body: 16px;
  --font-size-heading: 20px;
  --spacing-grid: 16px;
  --spacing-section: 24px;
  --spacing-field: 12px;

  /* Legacy color aliases — map old names onto editorial tokens */
  --color-text: var(--ink);
  --color-background: var(--paper);
  --color-border: var(--rule);
  --color-primary: var(--accent);
  --color-error: var(--accent);
  --color-success: var(--positive);

  /* Legacy *-rgb variants — recomputed to match resolved hex values */
  --color-text-rgb: 26 24 20;
  --color-primary-rgb: 184 68 42;
  --color-error-rgb: 184 68 42;
  --color-success-rgb: 74 107 58;
  --color-border-rgb: 200 191 177;
}
```

**Removed entirely:** the legacy `--font-stack` line. SC-1 covers presence of new tokens; FEATURE_SPEC §MH-1 covers the removal (only `global.css:45` consumes `--font-stack`, and the body rule below is rewritten to `var(--font-ui)`).

**Density values diverge from `tokens.css`:** the bundle's `:root` defines `--d-pad: 28px / --d-gap: 20px / --d-row: 56px` and overrides them in `[data-density="spacious"]`. FEATURE_SPEC §MH-1 mandates spacious values at `:root` with no `[data-density]` selectors. This deviation is intentional and pre-approved by analysis.

**Acceptance:** SC-1 (grep each token name in the post-edit file), SC-8 (`grep -E '\[data-(theme|accent|density)' src/styles/global.css` exits 1 / Scenario 6), Scenario 3 (legacy aliases resolve correctly in a live browser).

#### Edit 2.3 — `body` rule (currently lines 42–50)

Replace the entire `body { ... }` block. Keep `margin: 0` and `padding: var(--spacing-section)` so existing screens don't lose their 24px outer padding. Replace the rest with the editorial body rule from `tokens.css:79–88`, but preserve the existing `padding` per FEATURE_SPEC §MH-3 / R-6.

**New body block:**

```css
body {
  margin: 0;
  padding: var(--spacing-section);
  font-family: var(--font-ui);
  background: var(--paper);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.5;
  font-feature-settings: 'ss01', 'cv11';
  -webkit-font-smoothing: antialiased;
}
```

`--spacing-section` resolves to `24px`; legacy alias `--color-background` → `var(--paper)` would equally work but we use `--paper` directly because the body rule is editorial-native.

**Acceptance:** Scenario 1's seven assertions on `getComputedStyle(document.body)`. SC-9 / Scenario 20 — the new pytest test asserts the same seven values.

#### Edit 2.4 — `h1..h6` and `p` (currently lines 52–60) — UNCHANGED

These rules reference `--spacing-grid` and `--font-size-heading`, both kept-legacy tokens still defined. No edit.

#### Edit 2.5 — `.container`, `.header`, `.status`, `.saved-indicator`, `@keyframes fadeIn/fadeOut`, `.empty-state`, `.skeleton`, `@keyframes shimmer` (currently lines 65–122) — UNCHANGED

All layout-only or animation rules referenced verbatim by `FEATURE_SPEC §MH-6` under "Kept verbatim". No edit.

`.status` uses `var(--color-success)` and `.saved-indicator` uses `var(--color-success)` — both now resolve to `--positive`. Visually they shift from green `#008800` to editorial green `#4a6b3a`. This is **not** in the UX_DESIGN allowlist of intended deltas but it falls under the "legacy aliases resolve onto new editorial tokens" contract, so it is **expected**, not a regression. **Add this case to the inspector's manual checklist** (see Phase 3 below) so the human inspector doesn't flag it as a surprise.

#### Edit 2.6 — `.btn` and `.btn-primary` (currently lines 127–154)

Remove the legacy bodies entirely. Replace with the editorial bodies from `tokens.css:138–159`.

**New block (replaces lines 124–154; keep the `============ Buttons` section comment for navigability):**

```css
/* ============================================
   Buttons — editorial
   ============================================ */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  background: var(--card);
  color: var(--ink);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
  cursor: pointer;
  transition: all .15s;
}
.btn:hover { background: var(--paper-2); border-color: var(--ink-3); }

.btn-primary {
  background: var(--ink);
  color: var(--paper);
  border-color: var(--ink);
}
.btn-primary:hover { background: var(--ink-2); border-color: var(--ink-2); }

.btn-accent {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.btn-ghost {
  background: transparent;
  border-color: transparent;
  color: var(--ink-2);
}
.btn-ghost:hover { background: var(--paper-2); }
```

Note the deliberate dropping of `:focus { outline: 2px solid var(--color-primary); outline-offset: 1px; }` on `.btn`. The editorial body does not specify a focus outline. The browser default outline takes over. UX_DESIGN line 96–111 confirms this is the intended state and tracks the deferred `:focus-visible` decision.

#### Edit 2.7 — `.btn-add` (currently lines 156–159) — KEEP, MOVE

Keep the body unchanged (`padding: 4px 8px; font-size: 14px;`). Move it to sit immediately after the editorial `.btn-ghost` block so the section stays cohesive.

```css
.btn-add {
  padding: 4px 8px;
  font-size: 14px;
}
```

`.btn-add` is used by `src/components/Section.svelte:23` per FEATURE_SPEC R-5. It inherits `.btn`'s editorial colors automatically (the consumer applies both classes: `class="btn btn-add"` — verify with grep below).

**Pre-implementation check:** `grep -n 'btn-add' src/components/Section.svelte` should show the class is applied alongside `btn`. If the consumer uses `btn-add` alone, the editorial colors won't apply and the button will be unstyled — escalate via `note-capturer`. Section.svelte:23 readback is preferred over a wild grep so the line number is verified.

#### Edit 2.8 — Pills (NEW SECTION)

Insert a new section after `.btn-add` and before `/* Forms (shared) */`. Rules copied from `tokens.css:172–206`:

```css
/* ============================================
   Pills — editorial
   ============================================ */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 1px solid var(--rule);
  border-radius: 999px;
  color: var(--ink-3);
  background: transparent;
}
.pill-accent {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--accent-soft);
}
.pill-positive {
  color: var(--positive);
  border-color: var(--positive);
  background: var(--positive-soft);
}
.pill-warn {
  color: var(--warn);
  border-color: var(--warn);
  background: var(--warn-soft);
}
.pill-solid {
  background: var(--ink);
  color: var(--paper);
  border-color: var(--ink);
}
```

**Acceptance:** Scenarios 14 and 15.

#### Edit 2.9 — Typography primitives, rules, card (NEW SECTION)

Insert a new section **before** the `/* Reset */` block (so the editorial type primitives appear with the tokens at the top of the file, before the legacy layout sections). Rule bodies from `tokens.css:91–135`.

```css
/* ============================================
   Editorial typography primitives
   ============================================ */
.eyebrow {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-3);
  font-weight: 500;
}

.display {
  font-family: var(--font-display);
  font-weight: 400;
  letter-spacing: -0.01em;
  line-height: 1.05;
  color: var(--ink);
}

.serif-italic {
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
}

.num {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* ============================================
   Rules / dividers — editorial
   ============================================ */
.rule {
  border: 0;
  border-top: 1px solid var(--rule);
  margin: 0;
}
.rule-soft {
  border: 0;
  border-top: 1px solid var(--rule-soft);
  margin: 0;
}

/* ============================================
   Card — editorial
   ============================================ */
.card {
  background: var(--card);
  border: 1px solid var(--rule);
  border-radius: var(--r-md);
}
```

**Placement rationale:** typography primitives are foundational — they appear before reset/layout so a reader scanning the file sees vocabulary before layout. Order does not affect specificity (no selector collisions).

**Acceptance:** Scenarios 4, 7, 8, 9, 10.

#### Edit 2.10 — Coexistence comment + raw `input, textarea, select` rule (currently lines 191–211)

The current raw selector block at lines 191–211 stays. Immediately before it, insert the exact two-line `Note:` comment per FEATURE_SPEC §MH-6 / R-2:

```css
/* Note: the rules below style raw input/textarea/select for
   legacy forms; editorial `.input` / `.textarea` classes layer
   on top for new consumers. */
input,
textarea,
select {
  padding: 8px;
  font-size: var(--font-size-body);
  font-family: inherit;
  border: 1px solid var(--color-border);
  border-radius: 2px;
  background: var(--color-background);
  width: 100%;

  &:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: -1px;
    border-color: var(--color-primary);
  }

  &.error {
    border-color: var(--color-error);
  }
}
```

The body is unchanged from the current file. `var(--color-primary)` now resolves to `--accent` (terracotta), giving the focus-ring recolor described in UX_DESIGN intended-delta #5.

**Acceptance:** `grep -F 'Note: the rules below' src/styles/global.css` exits 0 with one match. Covers Scenario 19.

#### Edit 2.11 — `.input` and `.textarea` editorial classes (NEW)

Add **after** the raw `input, textarea, select` block. Rule bodies from `tokens.css:209–221`. The editorial classes are class-based; the raw selector is element-based. Both coexist by design (R-2 mitigation).

```css
/* ============================================
   Inputs — editorial
   ============================================ */
.input, .textarea {
  width: 100%;
  padding: 10px 12px;
  font-family: var(--font-ui);
  font-size: 13px;
  color: var(--ink);
  background: var(--paper);
  border: 1px solid var(--rule);
  border-radius: var(--r-sm);
  outline: none;
}
.input:focus, .textarea:focus { border-color: var(--ink); }
.textarea { resize: vertical; }
```

Drop the `font-family: var(--font-ui)` repeat on `.textarea` from `tokens.css:221` — `.input, .textarea` already declares it. The verbatim-copy obligation in FEATURE_SPEC §MH-4 is satisfied because the rule body content (computed result) is identical; we are not adding or removing any property, only deduplicating a redundant declaration. Scenarios 16 and 17 assert computed values, not raw source-order, so this is safe.

**Acceptance:** Scenarios 16, 17.

#### Edit 2.12 — Everything else (currently lines 218–350) — UNCHANGED

`.form`, `.form-row`, `.form-row-inline`, `label`, `textarea` min-height/resize raw rule, `.form-actions`, `.delete-link`, `.error-message`, `.form-error`, `.checkbox-row`, `.required`, `[aria-required]`, `.item-list`, `.item`, `.item-header`, `.item-title`, `.item-subtitle`, `.item-description`, `.edit-btn`, `@keyframes spin`, `@keyframes progress` — all kept verbatim per FEATURE_SPEC §MH-6.

One subtlety: the raw `textarea { min-height: 80px; resize: vertical; }` block at the **bottom** of the current file (lines 213–216) overlaps with the new editorial `.textarea { resize: vertical }` class. They don't conflict — the raw selector applies to every `<textarea>` regardless of class; the `.textarea` class duplicates `resize: vertical` for class-based consumers. Keep both; no edit.

---

### File 3 — `tests/test_design_tokens.py` (CREATE)

New file. Boots a static HTTP server on `public/`, opens Chromium via Playwright sync API, navigates to `/`, waits for fonts, asserts the seven body computed-style values from Scenario 1. Single test function, single Playwright session — the slice's one automated smoke test.

#### Test file structure

```python
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Smoke-test the editorial body restyle reaches the served bundle.

import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


PUBLIC_DIR = Path(__file__).parent.parent / "public"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def create_public_server(port):
    handler = type(
        "PublicHandler",
        (SimpleHTTPRequestHandler,),
        {"__init__": lambda self, *a, **kw: SimpleHTTPRequestHandler.__init__(self, *a, directory=str(PUBLIC_DIR), **kw)},
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture
def public_url():
    if not (PUBLIC_DIR / "build" / "bundle.css").exists():
        pytest.skip("public/build/bundle.css missing — run `bun run build` first")
    port = find_free_port()
    server = create_public_server(port)
    yield f"http://127.0.0.1:{port}/"
    server.shutdown()


def read_body_computed_styles(page):
    return page.evaluate("""() => {
        const computed = window.getComputedStyle(document.body);
        return {
            backgroundColor:     computed.backgroundColor,
            color:               computed.color,
            fontFamily:          computed.fontFamily,
            fontSize:            computed.fontSize,
            lineHeight:          computed.lineHeight,
            fontFeatureSettings: computed.fontFeatureSettings,
            webkitFontSmoothing: computed.getPropertyValue('-webkit-font-smoothing'),
        };
    }""")


def test_body_renders_editorial_tokens(public_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(public_url, wait_until="load")
            page.evaluate("() => document.fonts.ready")
            styles = read_body_computed_styles(page)
            context.close()
        finally:
            browser.close()

    assert styles["backgroundColor"] == "rgb(244, 241, 236)"
    assert styles["color"] == "rgb(26, 24, 20)"
    assert styles["fontFamily"].startswith('"Inter Tight"')
    assert styles["fontSize"] == "14px"
    assert styles["lineHeight"] == "21px"
    assert "ss01" in styles["fontFeatureSettings"]
    assert "cv11" in styles["fontFeatureSettings"]
    if styles["webkitFontSmoothing"]:
        assert styles["webkitFontSmoothing"] == "antialiased"
```

**Lean-code compliance review (self-check on each function name):**

| Function | Verb | Scope | Compliant? |
|---|---|---|---|
| `find_free_port` | `find` | `free_port` (2 words) | ✓ |
| `create_public_server` | `create` | `public_server` (2 words) | ✓ |
| `public_url` (pytest fixture) | (none) | — | Fixture name; pytest convention — fixtures name the resource they provide, not the action. Permitted exception, mirrors `client` and `setup_test_db` in `tests/conftest.py`. |
| `read_body_computed_styles` | `read` | `body_computed_styles` (3 words) | ✓ |
| `test_body_renders_editorial_tokens` | (none) | — | Pytest test convention `test_*`; permitted. |

`SimpleHTTPRequestHandler` and `ThreadingHTTPServer` are stdlib symbols — the file does not introduce new framework-suffixed names of our own.

**Open question 1 handled — `webkitFontSmoothing`:** the `getPropertyValue('-webkit-font-smoothing')` form is used (per docs-researcher recommendation). The final assertion is **gated on truthy return value** — if Chromium headless returns `""` we skip the assertion silently rather than fail. This preserves the smoke-test contract (Scenario 1 asserts the value when present) while not blocking CI on a non-standard property that may not be readable. The build phase's first headed run determines whether to remove the gate. RETROSPECTIVE captures the outcome.

**Open question 2 handled — `document.fonts.ready` in sync evaluate:** per docs-researcher, `page.evaluate` waits for returned Promises. We call it after `wait_until="load"` so the stylesheet is parsed; the fonts will be on the loading set. If on first run the assertion `fontFamily.startswith('"Inter Tight"')` fails because the fallback resolved instead, fall back to `page.wait_for_function("() => document.fonts.ready.then(() => true)")` as the docs-researcher's alternative. The plan does **not** preemptively use the alternative because the simpler `evaluate("() => document.fonts.ready")` is documented to suffice.

**Playwright binary guard:** the fixture skips the test when `public/build/bundle.css` is missing (the common failure mode in CI without a build step). It does **not** add a separate Chromium-binary guard because:

1. `services/pdf_generator.py:42` already uses Playwright in production code; the project assumes the binary is installed.
2. `tests/conftest.py:3` sets `PLAYWRIGHT_BROWSERS_PATH=0` which means Playwright looks for the system-installed Chromium.
3. If the binary is missing, the test fails with Playwright's own clear error message. Adding a wrapper guard duplicates work and obscures the real error.

**Acceptance:** `uv run pytest tests/test_design_tokens.py` exits 0. Covers SC-9, Scenario 1, Scenario 20.

---

### File 4 — `pyproject.toml` (NOT MODIFIED)

`playwright>=1.40.0` is already declared. `pytest>=8.0.0` is already declared. No new dependencies.

### File 5 — `rollup.config.js` (NOT MODIFIED)

`rollup-plugin-css-only` already emits `bundle.css` from imported CSS. `src/main.js:1` imports `./styles/global.css`. No build-config changes.

### File 6 — `src/components/**` (NOT MODIFIED)

The slice ships zero component edits. The legacy alias contract is the whole point.

### File 7 — `services/pdf_generator.py` (NOT MODIFIED)

The PDF generator inlines its own `templates/resume_base.css` (line 37) — it does not consume `src/styles/global.css`. PDF generation is unaffected by this slice.

---

## Execution order

1. Re-run the three pre-implementation grep checks. Stop and escalate if any diverges.
2. Edit `public/index.html` — add the three font `<link>` tags.
3. Edit `src/styles/global.css` top-down in the order listed under Edits 2.1 → 2.11. Keep a working copy of the file open in the editor; do not split the rewrite across multiple sessions.
4. Run `bun run build` and verify `grep -F -- '--paper: #f4f1ec' public/build/bundle.css` returns one match. Confirms SC-3 before test work.
5. Create `tests/test_design_tokens.py` with the structure above.
6. Run `uv run pytest tests/test_design_tokens.py -v`. Resolve `webkitFontSmoothing` open question if the assertion is hit.
7. Run the full suite: `uv run pytest`. Confirms SC-4 (no regression).
8. Manual: open the app in a browser via the project's standard dev workflow (`uv run uvicorn main:app --reload` then load `http://localhost:8000/`). Inspect against UX_DESIGN's verification checklist + Intended Visible Deltas allowlist.

## Test plan

| Test | Command | Maps to |
|---|---|---|
| Token & primitive presence (grep) | `grep -F -- '--paper: #f4f1ec' src/styles/global.css && grep -F '.eyebrow' src/styles/global.css && ...` (full list in CHECKLIST) | SC-1 |
| Fonts loaded (grep) | `grep -c 'fonts.googleapis.com' public/index.html` returns `2` | SC-2 |
| Bundle build | `bun run build && grep -F -- '--paper: #f4f1ec' public/build/bundle.css` | SC-3 |
| Existing tests still pass | `uv run pytest` | SC-4 |
| Browser smoke test | `uv run pytest tests/test_design_tokens.py` | SC-5, SC-9, Scenarios 1, 20 |
| No data-attribute selectors | `grep -cE '\[data-(theme\|accent\|density)' src/styles/global.css` returns `0` | SC-8, Scenario 6 |
| WARNING comment present | `grep -F 'WARNING (slice 1' src/styles/global.css` exits 0 | Scenario 18 |
| Coexistence comment present | `grep -F 'Note: the rules below' src/styles/global.css` exits 0 | Scenario 19 |
| Per-primitive visual contract | Inspector phase, manual computed-style checks in DevTools or Playwright REPL per UX_DESIGN gallery | SC-6, Scenarios 2–4, 7–17 |
| Network fonts | Inspector phase, manual DevTools Network filter | Scenario 5 |

Per-primitive computed-style assertions (Scenarios 2, 4, 7–17) are **deferred to the follow-up backlog item** `backlog/refined/design-system-tests-expansion.md` (already refined; sequenced after slice 2, before slice 3). This slice ships only the body-restyle assertion as the smoke test; richer coverage comes next.

## Risks (delta from FEATURE_SPEC)

The FEATURE_SPEC's R-1 through R-6 are addressed by the edit plan above. Two **implementation-phase risks** the spec did not flag:

- **IR-1: Order of `<link>` tags affects font-render-blocking.** The Google Fonts stylesheet must load before `bundle.css` to avoid a flash of fallback fonts on first paint. Plan addresses by inserting the three `<link>` tags **before** the existing bundle `<link>` in `<head>`. If this ordering is reversed, SC-5's "no FOIT" verification will fail on first load.
- **IR-2: Edit 2.1 (header rewrite) deviates from the analyze-phase claim that the WARNING comment sits "immediately after the existing single-line file-header comment."** The legacy single-line header is replaced by the two-line lean-code header; the WARNING comment sits after the lean-code header. This preserves the *spirit* (WARNING is at the top of the file, before `:root`) and the literal grep acceptance (`grep -F 'WARNING (slice 1'`). If plan-reviewer flags this as a contract violation, fall back to keeping the legacy single-line header **and** adding the lean-code header above it (3 comment lines total before WARNING). Either form passes the literal grep.

## Inspector phase preparation

UX_DESIGN line 207–215 gives the manual checklist already. Inspector should additionally check:

- **`.status` and `.saved-indicator` color drift** — both now resolve to `--positive #4a6b3a` (darker editorial green) instead of `#008800`. Expected, not a regression.
- **`.delete-link` and `.error-message` color drift** — both resolve to `--color-error` which aliases to `--accent` (terracotta). The WARNING block in `global.css` documents this intentionally; inspector should confirm error UI is visually distinguishable from primary CTAs *despite* both being terracotta. If indistinguishable in a critical flow (e.g. profile editor's "Are you sure?" confirmation), note for slice 2+ remediation but do not fail the slice.
- **`.form-error` background recompute** — `rgb(var(--color-error-rgb) / 0.05)` now resolves to a very light terracotta tint instead of light red. Expected.

## Open items (carried to RETROSPECTIVE)

1. `webkitFontSmoothing` headless readability — confirmed/disconfirmed during build phase test runs.
2. `:focus-visible` outline — UX_DESIGN explicitly defers; next focusable-surface slice (likely slice 2 — topbar) must close or carry forward.
3. `--shadow-card` ships unused — consumed by slices 7–8. Forward-use note already in FEATURE_SPEC.
4. `--color-error → --accent` discoverability — documented WARNING; per-slice migration planned in slices 2–9.
