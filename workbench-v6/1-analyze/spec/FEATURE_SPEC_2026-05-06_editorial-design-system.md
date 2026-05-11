# FEATURE_SPEC — editorial-design-system

**Date:** 2026-05-06
**Slug:** editorial-design-system
**Ceremony level:** M
**Slice:** 1 of 9 (foundation) in the editorial redesign initiative

## Confirmed root cause / motivation

The app currently exposes a generic six-variable token block in
`src/styles/global.css` (`--color-text`, `--color-background`,
`--color-primary`, `--color-error`, `--color-success`, `--color-border`)
plus an Apple-system `--font-stack`. This vocabulary is too narrow to
anchor the editorial redesign in `design-bundle/`. Slices 2–9 (topbar,
profile, resume preview, saved jobs, tailor, dashboard, kanban,
interview prep) all need:

- A paper / ink palette with multiple ink shades and rule colors.
- A serif display + sans UI + mono accent type stack.
- A spacious density scale (pad 36 / gap 28 / row 64).
- Reusable primitive classes (eyebrow, display, card, btn variants,
  pill variants, input, textarea).

Without these tokens, every downstream slice would either redefine its
own scoped variables (drift) or be blocked. This slice unblocks the
chain by porting `design-bundle/project/tokens.css` into
`src/styles/global.css`, plus loading the Google Fonts in
`public/index.html`.

Existing components in `src/components/` (ResumeView, profile editor,
preferences sidebar, etc.) cannot be restyled in this slice — that work
is split across slices 2–9. They keep rendering via **legacy aliases**:
the old variable names stay defined in `:root` but their values are
remapped onto the new editorial tokens (e.g. `--color-text: var(--ink)`,
`--color-background: var(--paper)`, `--color-primary: var(--accent)`).

## Persona

**Slice 2–9 implementer.** The developer who, after this slice ships,
opens any Svelte component in `src/components/` and writes
`<button class="btn btn-accent">` or `<span class="eyebrow">SECTION</span>`
without having to import or define anything. They expect the global
token names and primitive class names to match `tokens.css` exactly —
that's the contract this slice publishes.

## Core pain point

**No design vocabulary yet.** Today there is one source of truth for
the editorial design (`design-bundle/project/tokens.css`) but it is
gitignored reference material, not part of the build. Slices 2–9 cannot
import it. This slice copies it into the build pipeline so subsequent
slices can rely on `var(--paper)`, `var(--ink)`, `.card`, `.btn-accent`,
etc., compiling globally.

## Must-haves

1. **Token block.** `src/styles/global.css` exposes — at `:root`, with no
   `[data-theme]`/`[data-accent]`/`[data-density]` selectors:
   - **Paper:** `--paper #f4f1ec`, `--paper-2 #ece7df`, `--paper-3 #e0d9cd`.
   - **Ink:** `--ink #1a1814`, `--ink-2 #3a342c`, `--ink-3 #6b6358`,
     `--ink-4 #9c9387`.
   - **Rule:** `--rule #c8bfb1`, `--rule-soft #ddd5c7`.
   - **Card:** `--card #fbfaf6`.
   - **Accent:** `--accent #b8442a`, `--accent-soft #e9c8bd`.
   - **Status:** `--positive #4a6b3a`, `--positive-soft #d6dec9`,
     `--warn #a07024`, `--warn-soft #ead8b6`.
   - **Density (spacious baked in):** `--d-pad 36px`, `--d-gap 28px`,
     `--d-row 64px`.
   - **Radius:** `--r-sm 2px`, `--r-md 4px`, `--r-lg 6px`.
   - **Shadow:** `--shadow-card: 0 1px 0 rgba(26,24,20,0.04), 0 12px 32px -16px rgba(26,24,20,0.18)`.
     **Forward-use note:** `--shadow-card` is defined for slice 7
     (dashboard cards) and slice 8 (kanban columns). No primitive in
     this slice consumes it. The token ships now so downstream slices
     do not need a foundation-slice patch.
   - **Type stacks:** `--font-display`, `--font-serif`, `--font-ui`,
     `--font-mono` per `tokens.css` exactly.
   - **Kept legacy (non-color) tokens — values unchanged:**
     `--font-size-body: 16px`, `--font-size-heading: 20px`,
     `--spacing-grid: 16px`, `--spacing-section: 24px`,
     `--spacing-field: 12px`. These remain in `:root` because
     `src/components/` references them 73 times (verified by
     `grep -rn 'var(--\(spacing\|font-size\)' src/components/ | wc -l`).
     The legacy `--font-stack` is removed: only `global.css:45` (the
     body rule) consumes it, and that line is rewritten to
     `var(--font-ui)`. No alias for `--font-stack` is needed.

2. **Fonts loaded.** `public/index.html` includes a `<link>` to
   `https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700;9..144,800&family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap`
   plus the two `preconnect` links Google recommends.

3. **Body restyle.** The `body` rule in `global.css` switches to
   `font-family: var(--font-ui)`, `background: var(--paper)`,
   `color: var(--ink)`, `font-size: 14px`, `line-height: 1.5`,
   `font-feature-settings: 'ss01', 'cv11'`, plus
   `-webkit-font-smoothing: antialiased`. The current
   `padding: var(--spacing-section)` is preserved (legacy alias still
   resolves) so component layout doesn't shift.

4. **Primitive classes.** `global.css` defines (with rule bodies copied
   verbatim from `tokens.css`):
   - `.eyebrow`, `.display`, `.serif-italic`, `.num`
   - `.rule`, `.rule-soft`
   - `.card`
   - `.btn`, `.btn-primary`, `.btn-accent`, `.btn-ghost`
   - `.pill`, `.pill-accent`, `.pill-positive`, `.pill-warn`,
     `.pill-solid`
   - `.input`, `.textarea`

5. **Legacy color aliases.** The six legacy color variables and their
   `*-rgb` variants stay defined in `:root` but their values are
   remapped:
   - `--color-text: var(--ink);`
   - `--color-background: var(--paper);`
   - `--color-border: var(--rule);`
   - `--color-primary: var(--accent);`
   - `--color-error: var(--accent);` — see "Known compromise" paragraph
     below.
   - `--color-success: var(--positive);`
   - `*-rgb` variants updated to match the new resolved hex values:
     `--color-text-rgb: 26 24 20`, `--color-primary-rgb: 184 68 42`,
     `--color-success-rgb: 74 107 58`, `--color-error-rgb: 184 68 42`,
     `--color-border-rgb: 200 191 177`.

   ### Known compromise — `--color-error` aliased to `--accent`

   The editorial palette in `tokens.css` ships no dedicated error
   token (`--accent`, `--positive`, `--warn` only). Slice 1 aliases
   `--color-error: var(--accent)` so existing `.form-error`,
   `.error-message`, `<input>.error` consumers keep rendering — but
   they now render in **terracotta**, the same color as primary CTAs.
   This is a temporary discoverability hazard.

   **Mandatory mitigation — file-header warning.** Add this exact
   comment block to the top of `src/styles/global.css`, immediately
   after the existing single-line file-header comment and before any
   `:root` rule:

   ```css
   /* WARNING (slice 1 / editorial-design-system, 2026-05-06):
      --color-error currently resolves to --accent (terracotta).
      The editorial palette has no dedicated error token. Do NOT
      introduce new error semantics on this alias — replace it with
      a slice-specific token before adding any new validation UI. */
   ```

   The acceptance criterion is the literal presence of these five
   comment lines (grep `WARNING (slice 1`).

6. **Existing legacy rules untouched.** Everything below the token
   block in `global.css` (the existing `.btn`/`.btn-primary` rules,
   `.form`, `.item-list`, animations, etc.) **must be replaced** by the
   editorial primitives where the class names collide (`.btn`,
   `.btn-primary`, `.input`, `.textarea`), and **kept** where they are
   layout-only and non-colliding (`.container`, `.header`, `.form`,
   `.form-row`, `.item`, `.delete-link`, `.empty-state`, `.skeleton`,
   `@keyframes`). Collisions are resolved by the editorial version
   winning (last-defined-wins inside `global.css`).

   - **Replaced (collision):** `.btn`, `.btn-primary`, `.input`,
     `.textarea`. The legacy bodies are removed; the editorial bodies
     from `tokens.css` are the only definition.

     **Verification (replayable):** running
     `grep -rnE 'class="[^"]*\b(input|textarea)\b[^"]*"' src/components/`
     in this slice's working tree returns only `title-input`,
     `jd-input`, `file-input` — all unrelated tokens. No existing
     component uses bare `.input` / `.textarea` as a class, so the
     editorial class additions do not disturb forms, which use raw
     `input/textarea/select` selectors handled by the kept legacy
     block. The build-phase implementer **must re-run this command
     before editing global.css** to confirm no new consumers appeared
     between analyze and build; if any match other than the three
     unrelated tokens appears, escalate via `note-capturer`.

     **Coexistence note (R-2 mitigation).** The raw selector block at
     the bottom of `global.css` (`input, textarea, select { ... }`)
     stays. The editorial `.input` / `.textarea` classes layer **on
     top** for new consumers. Add this exact two-line comment
     immediately before the raw selector block:

     ```css
     /* Note: the rules below style raw input/textarea/select for
        legacy forms; editorial `.input` / `.textarea` classes layer
        on top for new consumers. */
     ```

     Acceptance: grep `Note: the rules below` returns one match.
   - **Kept (extension on top of editorial `.btn`):** `.btn-add` — used
     by `src/components/Section.svelte:23`. Body unchanged
     (`padding: 4px 8px; font-size: 14px`); inherits the editorial
     `.btn` colors and border.
   - **Kept verbatim:** `.container`, `.header`, `.status`,
     `.saved-indicator`, `.empty-state`, `.skeleton`, `.form`,
     `.form-row`, `.form-row-inline`, `.form-actions`, `label`,
     `input/textarea/select` raw selector, `.delete-link`,
     `.error-message`, `.form-error`, `.checkbox-row`, `.required`,
     `.item-list`, `.item`, `.item-header`, `.item-title`,
     `.item-subtitle`, `.item-description`, `.edit-btn`, all
     `@keyframes`.

7. **No data-attribute selectors.** Grep over the final
   `src/styles/global.css` returns zero matches for `[data-theme`,
   `[data-accent`, `[data-density`. Dark theme, accent variants, and
   density variants from the bundle are intentionally not ported.

## Out of scope

- Restyling `ResumeView`, profile editor, preferences sidebar, or any
  other component — handled in slices 2–9.
- Removing the legacy alias variables — happens per consumer slice.
- Live tweaks panel, dark theme, sidebar nav, mobile/responsive.
- Adding new error semantics distinct from accent (the `--color-error`
  alias intentionally points at accent for now).

## Success criteria

- **SC-1.** `src/styles/global.css` defines every token in §Must-haves
  point 1 at `:root`, plus every primitive class in point 4. Verified
  by grep.
- **SC-2.** `public/index.html` contains exactly one `<link>` to
  `fonts.googleapis.com/css2?family=...` matching the bundle URL, plus
  the `preconnect` links to `fonts.googleapis.com` and
  `fonts.gstatic.com`.
- **SC-3.** `bun run build` succeeds with exit code 0; the emitted
  `public/build/bundle.css` contains the literal string `--paper:
  #f4f1ec` (one grep is sufficient — if it's there, the editorial
  token block reached the bundle).
- **SC-4.** `uv run pytest` still passes (no regressions in component
  behavior; CSS changes don't affect Python tests but a green run
  confirms nothing else slipped).
- **SC-5.** Loading the app in a browser shows: paper background
  (`#f4f1ec`), ink body text (`#1a1814`), Inter Tight as the body
  font (verifiable via DevTools → Computed → font-family). The four
  font families load over the network without console errors.
- **SC-6.** A scratch render — a temporary route or inspector-driven
  injection — of every primitive class enumerated in MH-4 visually
  matches `design-bundle/project/MyCV.html`. Per-primitive computed
  values are asserted in BDD scenarios 7–17 below.
- **SC-7.** Existing screens (the resume view at `/`) still render
  with no broken layouts. "Broken" is bounded by the **Intended
  visible deltas** allowlist in UX_DESIGN: any visible change outside
  that allowlist is a regression. The five intended deltas (body bg,
  body color, body font, `.btn-primary` recolor, focus-ring recolor)
  are not regressions; anything else (element collapse, overlap, lost
  padding, lost margin, missing background where one existed) is.
- **SC-8.** `grep -E '\[data-(theme|accent|density)' src/styles/global.css`
  returns zero matches.
- **SC-9.** The new pytest test `tests/test_design_tokens.py` (added
  by this slice) passes via `uv run pytest tests/test_design_tokens.py`.
  It boots a static HTTP server on `public/`, opens Playwright (Python
  binding, already a project dep), navigates to `/`, and asserts
  body's computed background `rgb(244, 241, 236)`, color
  `rgb(26, 24, 20)`, font-family starts with `"Inter Tight"`,
  font-size `14px`, line-height `21px` (1.5 of 14). This is the slice's
  one automated smoke test; richer per-primitive coverage is deferred
  to `backlog/refined/design-system-tests-expansion.md`.

## BDD scenarios

### Scenario 1 — Body restyle reaches the browser

**Given** the new editorial `global.css` is built and served,
**When** the user opens the app at `http://localhost:8080`,
**Then** `getComputedStyle(document.body).backgroundColor` equals
`rgb(244, 241, 236)` (i.e. `#f4f1ec`),
**And** `getComputedStyle(document.body).color` equals
`rgb(26, 24, 20)` (i.e. `#1a1814`),
**And** `getComputedStyle(document.body).fontFamily` starts with
`"Inter Tight"`,
**And** `getComputedStyle(document.body).fontSize` equals `14px`,
**And** `getComputedStyle(document.body).lineHeight` equals `21px`
(1.5 of 14),
**And** `getComputedStyle(document.body).fontFeatureSettings`
contains the substring `"ss01"` and the substring `"cv11"`,
**And** `getComputedStyle(document.body).webkitFontSmoothing` equals
`antialiased`.

### Scenario 2 — Primitive class is globally available

**Given** `global.css` is loaded,
**When** a developer drops
`<button class="btn btn-accent">Apply</button>` into any Svelte
component and renders it,
**Then** `getComputedStyle(button).backgroundColor` equals
`rgb(184, 68, 42)` (i.e. `--accent #b8442a`),
**And** `getComputedStyle(button).color` equals `rgb(255, 255, 255)`,
**And** `getComputedStyle(button).borderRadius` equals `2px`.

### Scenario 3 — Legacy color aliases resolve correctly

**Given** the new `global.css`,
**When** a test page reads
`getComputedStyle(document.documentElement)` for each legacy custom
property,
**Then** the resolved values are:

- `--color-text` → `rgb(26, 24, 20)` (i.e. `--ink`)
- `--color-background` → `rgb(244, 241, 236)` (i.e. `--paper`)
- `--color-border` → `rgb(200, 191, 177)` (i.e. `--rule`)
- `--color-primary` → `rgb(184, 68, 42)` (i.e. `--accent`)
- `--color-error` → `rgb(184, 68, 42)` (i.e. `--accent`, per
  Known Compromise)
- `--color-success` → `rgb(74, 107, 58)` (i.e. `--positive`)

**And** the `*-rgb` triplets resolve to the matching space-separated
form:

- `--color-text-rgb` → `26 24 20`
- `--color-primary-rgb` → `184 68 42`
- `--color-error-rgb` → `184 68 42`
- `--color-success-rgb` → `74 107 58`
- `--color-border-rgb` → `200 191 177`

This protects alpha-overlay patterns like
`rgb(var(--color-error-rgb) / 0.05)` used in `.form-error`.

### Scenario 4 — Editorial typography pair renders

**Given** a developer drops
`<span class="eyebrow">Section</span><h1 class="display">Headline</h1>`,
**When** the component mounts,
**Then** the eyebrow's computed `font-family` starts with
`"JetBrains Mono"` and `text-transform` is `uppercase` and
`letter-spacing` is `0.12em` and `color` resolves to
`rgb(107, 99, 88)` (i.e. `--ink-3`),
**And** the heading's computed `font-family` starts with
`"Instrument Serif"` and `letter-spacing` is `-0.01em`.

### Scenario 5 — Fonts loaded over the network

**Given** the app is loaded in a fresh browser session,
**When** the user opens DevTools → Network and filters by
`fonts.googleapis.com` or `fonts.gstatic.com`,
**Then** at least one stylesheet request to `fonts.googleapis.com`
returns 200,
**And** at least one font-file request to `fonts.gstatic.com` returns
200 for each of Instrument Serif, Fraunces, Inter Tight, JetBrains
Mono.

### Scenario 6 — No data-attribute selectors leaked

**Given** the new `global.css`,
**When** running `grep -E '\[data-(theme|accent|density)' src/styles/global.css`,
**Then** the command exits with code 1 (no matches).

### Scenario 7 — `.serif-italic` renders editorial italic

**Given** a developer drops `<em class="serif-italic">italic</em>`,
**When** the element mounts,
**Then** `font-family` starts with `"Instrument Serif"`
**And** `font-style` is `italic`
**And** `font-weight` is `400`.

### Scenario 8 — `.num` enables tabular numerics

**Given** `<span class="num">12345</span>`,
**When** the element mounts,
**Then** `font-family` starts with `"JetBrains Mono"`
**And** `font-variant-numeric` contains `tabular-nums`.

### Scenario 9 — `.rule` and `.rule-soft` are 1px horizontal dividers

**Given** `<hr class="rule">` and `<hr class="rule-soft">`,
**When** both elements are rendered,
**Then** `.rule` computed `border-top-width` is `1px`,
`border-top-style` is `solid`, `border-top-color` is
`rgb(200, 191, 177)`, `margin-top` and `margin-bottom` are `0px`,
**And** `.rule-soft` computed `border-top-color` is
`rgb(221, 213, 199)`.

### Scenario 10 — `.card` matches editorial card

**Given** `<div class="card">content</div>`,
**When** rendered,
**Then** `background-color` is `rgb(251, 250, 246)`,
**And** `border` is `1px solid rgb(200, 191, 177)`,
**And** `border-radius` is `4px`.

### Scenario 11 — `.btn` (default) renders editorial neutral button

**Given** `<button class="btn">Action</button>`,
**When** rendered,
**Then** `background-color` is `rgb(251, 250, 246)` (`--card`),
**And** `color` is `rgb(26, 24, 20)` (`--ink`),
**And** `border` is `1px solid rgb(200, 191, 177)` (`--rule`),
**And** `padding` is `9px 14px`,
**And** `font-family` starts with `"Inter Tight"`,
**And** `font-size` is `13px`,
**And** `font-weight` is `500`,
**And** `border-radius` is `2px`.

### Scenario 12 — `.btn-primary` renders ink-filled

**Given** `<button class="btn btn-primary">Apply</button>`,
**When** rendered,
**Then** `background-color` is `rgb(26, 24, 20)` (`--ink`),
**And** `color` is `rgb(244, 241, 236)` (`--paper`),
**And** `border-color` is `rgb(26, 24, 20)` (`--ink`).

### Scenario 13 — `.btn-ghost` renders transparent

**Given** `<button class="btn btn-ghost">Cancel</button>`,
**When** rendered,
**Then** `background-color` is `rgba(0, 0, 0, 0)` (transparent),
**And** `border-color` is `rgba(0, 0, 0, 0)` (transparent),
**And** `color` is `rgb(58, 52, 44)` (`--ink-2`).

### Scenario 14 — `.pill` (default) renders neutral tag

**Given** `<span class="pill">tag</span>`,
**When** rendered,
**Then** `background-color` is `rgba(0, 0, 0, 0)` (transparent),
**And** `color` is `rgb(107, 99, 88)` (`--ink-3`),
**And** `border` is `1px solid rgb(200, 191, 177)` (`--rule`),
**And** `border-radius` is `999px`,
**And** `font-family` starts with `"JetBrains Mono"`,
**And** `font-size` is `10px`,
**And** `text-transform` is `uppercase`,
**And** `letter-spacing` is `0.06em`.

### Scenario 15 — `.pill` variants apply correct color triple

**Given** four pill variants — `.pill-accent`, `.pill-positive`,
`.pill-warn`, `.pill-solid` — each on a `<span class="pill ...">`,
**When** rendered,
**Then** the computed `color`, `background-color`, and
`border-color` triple is:

- `.pill-accent` → color `rgb(184, 68, 42)`, bg `rgb(233, 200, 189)`,
  border `rgb(184, 68, 42)`
- `.pill-positive` → color `rgb(74, 107, 58)`, bg `rgb(214, 222, 201)`,
  border `rgb(74, 107, 58)`
- `.pill-warn` → color `rgb(160, 112, 36)`, bg `rgb(234, 216, 182)`,
  border `rgb(160, 112, 36)`
- `.pill-solid` → color `rgb(244, 241, 236)`, bg `rgb(26, 24, 20)`,
  border `rgb(26, 24, 20)`.

### Scenario 16 — `.input` default and focus

**Given** `<input class="input">`,
**When** rendered (no focus),
**Then** `background-color` is `rgb(244, 241, 236)` (`--paper`),
**And** `color` is `rgb(26, 24, 20)` (`--ink`),
**And** `border` is `1px solid rgb(200, 191, 177)` (`--rule`),
**And** `border-radius` is `2px`,
**And** `padding` is `10px 12px`,
**And** `outline-style` is `none`.

**Given** the same `<input class="input">` is then focused,
**When** focus is acquired,
**Then** `border-color` becomes `rgb(26, 24, 20)` (`--ink`)
**And** `outline-style` remains `none`.

### Scenario 17 — `.textarea` default and resize

**Given** `<textarea class="textarea"></textarea>`,
**When** rendered,
**Then** every computed value from Scenario 16's default state
applies identically,
**And** `resize` is `vertical`.

### Scenario 18 — File-header warning is present

**Given** the new `global.css`,
**When** running `grep -F 'WARNING (slice 1' src/styles/global.css`,
**Then** the command exits with code 0 and prints the line.

### Scenario 19 — Coexistence comment is present

**Given** the new `global.css`,
**When** running `grep -F 'Note: the rules below' src/styles/global.css`,
**Then** the command exits with code 0 and prints the line.

### Scenario 20 — Smoke test asserts body restyle

**Given** the slice's new test file `tests/test_design_tokens.py`,
**When** running `uv run pytest tests/test_design_tokens.py`,
**Then** the run exits with code 0,
**And** every body-restyle assertion from Scenario 1 is asserted by
the test.

## Risks

- **R-1: Class-name collision.** `global.css` already defines `.btn`
  and `.btn-primary` with old semantics; the editorial version
  replaces them. Existing components using these classes (search:
  `grep -rn 'class="[^"]*btn' src/components/`) will inherit the new
  visual but the rule order in `global.css` decides who wins. Mitigation:
  remove legacy bodies entirely; only the editorial version exists.
- **R-2: Input raw-selector vs `.input` class.** `global.css` styles
  `input, textarea, select { ... }` as raw selectors today. The
  editorial `.input` class is class-based, not selector-based, so it
  won't override the raw selector unless an `<input>` carries
  `class="input"`. Both coexist: raw `input` styling stays for legacy
  forms; `.input` class adds editorial rules on top for new consumers.
  **Mitigation (specific):** the exact two-line `/* Note: the rules
  below... */` comment defined in MH-6's "Coexistence note" is added
  immediately before the raw selector block. Acceptance is the literal
  grep match `Note: the rules below`.
- **R-3: `--color-error` aliased to `--accent`.** Conflates error and
  accent visually until each consumer migrates to a slice-specific
  semantic. **Mitigation (specific):** the five-line `/* WARNING
  (slice 1 ... */` comment defined in MH-5's "Known compromise"
  paragraph is added at the top of `global.css` immediately after the
  existing file-header comment. Acceptance is the literal grep match
  `WARNING (slice 1`.
- **R-4: Google Fonts CDN.** External request adds ~200ms first-paint
  on first load; subsequent loads are cached. Acceptable for desktop
  app; not a blocker. No offline-first requirement in the project.
- **R-5: `.btn-add` retained.** `Section.svelte:23` still uses it.
  Keep the rule body unchanged so the smaller padding survives; it
  inherits the new editorial colors automatically through `.btn`.
- **R-6: Body padding alias.** Current `body` has
  `padding: var(--spacing-section)` (24px). The editorial body rule
  in `tokens.css` has no padding. We keep `padding: var(--spacing-section)`
  to avoid layout collapse in unrestyled screens; the legacy
  `--spacing-section` variable also stays in `:root`.
