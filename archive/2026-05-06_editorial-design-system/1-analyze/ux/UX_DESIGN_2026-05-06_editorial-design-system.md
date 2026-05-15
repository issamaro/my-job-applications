# UX_DESIGN — editorial-design-system

**Date:** 2026-05-06
**Slug:** editorial-design-system
**UX direction:** Preserve current patterns
**Shape:** No new screens. This document is a **primitive-states gallery** —
it specifies the visual contract each primitive class publishes to slices
2–9 implementers. Source of truth for every rule body is
`design-bundle/project/tokens.css`.

## Why no screens

The slice ships zero new routes. Existing routes (the resume view at `/`
and the profile editor) keep rendering through legacy aliases — they
visibly shift (paper background, ink text, Inter Tight body, ink-filled
primary buttons) but the layout, copy, navigation, and information
architecture stay identical. Per-screen redesign is the responsibility
of slices 2–9.

## Intended visible deltas (vs. pre-slice baseline)

The slice does not redesign any screen, but five propagating changes
do reach the user the moment slice 1 ships. **These are the design's
purpose, not regressions** — the inspect phase (Q4) must treat them
as expected, not flag them as failures:

1. **Body background** — flips from white (`#ffffff`) to paper
   (`#f4f1ec`). Visible everywhere.
2. **Body text color** — flips from `#1a1a1a` to ink (`#1a1814`).
   Marginal hue shift; not noticeable in isolation but adds
   warmth in combination with paper.
3. **Body font** — flips from `-apple-system, BlinkMacSystemFont,
   "Segoe UI", Roboto, sans-serif` to `"Inter Tight", -apple-system,
   ...`. Visible on every page once the Google Fonts CSS resolves.
4. **`.btn-primary` color** — every existing consumer flips from
   blue (`#0066cc`) to ink (`#1a1814`). Specifically affects:
   - `ResumeView.svelte` — Download button.
   - `WorkExperience.svelte` — Save buttons (×2 occurrences).
   - `Education.svelte` — Save buttons (×2).
   - `Skills.svelte` — Add button.
   - `ResumeGenerator.svelte` — two primary buttons.
5. **Form input focus rings** — flip from blue (`#0066cc`,
   `var(--color-primary)`) to terracotta (`#b8442a`) because
   `--color-primary` aliases to `--accent`. Visible on the profile
   editor form, the resume edit inputs, the saved-jobs edit input,
   and any modal text input.

**Allowlist contract.** Anything outside this list of five that
visibly changed after slice 1 ships is a regression. Examples that
would be regressions: a button lost its padding, a list collapsed
to zero gap, an error message lost its red background entirely, the
delete-link text disappeared. The inspect phase scripts test each
of these explicitly via the BDD scenarios and SC-7.

## Primitive-states gallery

Each primitive below is a class that any Svelte component can apply
after this slice ships. The "states" column lists every visual state
the rule body covers — primitives without explicit hover/focus states
fall back to whatever the underlying element does (e.g. `.eyebrow` is
just typography, no hover semantics).

The "verification" column is what an inspector or test should observe
to call the primitive correct.

### Typography primitives

| Class | Default | States | Verification |
|-------|---------|--------|--------------|
| `.eyebrow` | JetBrains Mono 10px, uppercase, letter-spacing 0.12em, color `--ink-3 #6b6358`, weight 500 | (none — text-only) | `font-family` starts with `"JetBrains Mono"`, `text-transform` = `uppercase`, `letter-spacing` = `0.12em`, `color` resolves to `rgb(107, 99, 88)` |
| `.display` | Instrument Serif (fallback Fraunces, Georgia), weight 400, letter-spacing -0.01em, line-height 1.05, color `--ink` | (none — text-only) | `font-family` starts with `"Instrument Serif"`, `letter-spacing` = `-0.01em`, `line-height` ≈ `1.05` |
| `.serif-italic` | Same `--font-display` stack, italic, weight 400 | (none) | `font-family` starts with `"Instrument Serif"`, `font-style` = `italic` |
| `.num` | JetBrains Mono, `font-variant-numeric: tabular-nums` | (none) | `font-family` starts with `"JetBrains Mono"`, `font-variant-numeric` includes `tabular-nums` |

### Rules / dividers

| Class | Default | Verification |
|-------|---------|--------------|
| `.rule` | `border: 0; border-top: 1px solid var(--rule); margin: 0` (color `#c8bfb1`) | A horizontal `<hr class="rule">` is exactly 1px tall, color `rgb(200, 191, 177)`, no margin |
| `.rule-soft` | same as `.rule` but border-top color `var(--rule-soft)` `#ddd5c7` | Same shape, color `rgb(221, 213, 199)` |

### Card

| Class | Default | Verification |
|-------|---------|--------------|
| `.card` | background `--card #fbfaf6`, border `1px solid var(--rule)`, radius `var(--r-md)` (4px) | `background` = `rgb(251, 250, 246)`, `border` = `1px solid rgb(200, 191, 177)`, `border-radius` = `4px` |

### Buttons (`.btn` and variants)

All buttons share: `display: inline-flex; align-items: center; gap: 8px;
padding: 9px 14px; font-family: var(--font-ui); font-size: 13px;
font-weight: 500; cursor: pointer; transition: all .15s; border-radius: var(--r-sm)` (2px).

| Class | Default | Hover | Focus | Disabled |
|-------|---------|-------|-------|----------|
| `.btn` | bg `--card`, color `--ink`, border `--rule` | bg `--paper-2`, border `--ink-3` | (browser default — preserved by the slice; revisit per consumer) | (browser default `:disabled` — opacity not specified by `tokens.css`; component owners decide) |
| `.btn-primary` | bg `--ink`, color `--paper`, border `--ink` | bg `--ink-2 #3a342c`, border `--ink-2` | (browser default) | (component owners decide) |
| `.btn-accent` | bg `--accent #b8442a`, color `white`, border `--accent` | (no explicit hover in `tokens.css`; transition covers any consumer-added hover) | (browser default) | (component owners decide) |
| `.btn-ghost` | bg `transparent`, border `transparent`, color `--ink-2` | bg `--paper-2` | (browser default) | (component owners decide) |

**Empty / loading / success / error framing.** Buttons are interaction
primitives, not screens — they don't have empty/loading/error states
of their own. Consumers wrap them in component-level state. This slice
publishes only the four visual variants above.

**Accessibility note (deferred — tracked).** `tokens.css` does not
define a `:focus-visible` outline. The browser default outline is
preserved. A future slice should add a slice-level `:focus-visible`
style using `--accent` once the focus visibility contract is decided
across the app. This slice does **not** add one to avoid baking an
arbitrary choice into the foundation.

**Tracking:** captured in this slice's RETROSPECTIVE under "Deferred
decisions" and in `design-bundle/SLICE_INDEX.md` under "Known
compromises carried by slice 1". The next slice that adds new
focusable surfaces (likely slice 2 — topbar nav) must either close
the deferral or carry it forward explicitly.

### Pills

All pills share: `display: inline-flex; align-items: center; gap: 6px;
padding: 3px 9px; font-family: var(--font-mono); font-size: 10px;
letter-spacing: 0.06em; text-transform: uppercase; border-radius: 999px;
border: 1px solid var(--rule)`.

| Class | Default |
|-------|---------|
| `.pill` | color `--ink-3`, bg `transparent`, border `--rule` |
| `.pill-accent` | color `--accent`, bg `--accent-soft #e9c8bd`, border `--accent` |
| `.pill-positive` | color `--positive #4a6b3a`, bg `--positive-soft #d6dec9`, border `--positive` |
| `.pill-warn` | color `--warn #a07024`, bg `--warn-soft #ead8b6`, border `--warn` |
| `.pill-solid` | color `--paper`, bg `--ink`, border `--ink` |

Verification: each variant's three computed values (`color`,
`background-color`, `border-color`) match the table.

### Inputs

| Class | Default | Focus |
|-------|---------|-------|
| `.input` | width 100%, padding `10px 12px`, font `--font-ui` 13px, color `--ink`, bg `--paper`, border `--rule`, radius `--r-sm` (2px), `outline: none` | border-color `--ink` |
| `.textarea` | same as `.input` plus `resize: vertical` | same as `.input` focus |

Verification: focusing a `.input` swaps the border to ink without
showing a default browser outline (because the rule sets
`outline: none`).

**Accessibility note.** `outline: none` removes browser focus indicator
in favor of the border swap. This is consistent with `tokens.css` and
the editorial aesthetic. A future slice should add a complementary
`box-shadow: 0 0 0 2px var(--accent-soft)` on focus if testing reveals
poor contrast for keyboard users.

## Implicit empty/loading/success/error states for the slice itself

The slice has no UI surface, but the **app as a whole** has implicit
states because of body restyle and font loading:

- **Empty / first paint (font swap).** Fonts load with `display=swap`
  in the Google Fonts URL. First paint shows `Georgia` (display
  fallback) and system sans (UI fallback) before the editorial fonts
  arrive. This is acceptable and matches the bundle's choice. **Copy:**
  none. **Verification:** no FOIT (flash of invisible text) — text is
  always readable.
- **Loading (network).** If `fonts.googleapis.com` is unreachable,
  the body falls through to `Georgia, serif` for `.display` and
  `-apple-system, BlinkMacSystemFont, sans-serif` for `--font-ui`.
  The app is fully usable. **Copy:** none. **Verification:** disable
  network in DevTools, reload — every primitive still legible with
  fallback fonts.
- **Success.** Default. The four font families load, body shows paper
  background + ink text + Inter Tight, all primitives match
  `tokens.css`. **Verification:** SC-1 through SC-8 in FEATURE_SPEC.
- **Error.** No app-level error state for this slice. CSS parse
  failures would surface as unstyled body, which dev tooling catches
  during build (`bun run build` would still succeed but the bundle
  would emit a warning). **Verification:** `bun run build` exits 0
  with no `parse` warnings in stderr.

## Keyboard navigation map

The slice changes no tab order, no focus trapping, no shortcut
bindings. Existing forms keep their existing keyboard behavior. The
only keyboard-visible change is that focus rings on legacy
`<input>`/`<textarea>` (still styled by the kept raw selector at the
bottom of `global.css`) keep their existing 2px outline ring in
`var(--color-primary)` — which now resolves to `--accent` (terracotta)
instead of blue. That is the only deliberate keyboard-affordance
change in this slice.

## Verification checklist (UI-side)

For each primitive class in the gallery:

- [ ] Insert one element into a scratch page (or DevTools "Edit as
      HTML") and confirm computed-style values match the verification
      column.
- [ ] Confirm `font-family` chains include the expected first family
      (Inter Tight / Instrument Serif / JetBrains Mono).
- [ ] For `.btn` variants: hover state changes background as
      specified (where defined) within ~150ms.
- [ ] For `.pill` variants: all three of `color`, `background-color`,
      `border-color` match the table.
- [ ] For `.input` and `.textarea`: focusing the field swaps the
      border to `--ink` without revealing a browser outline.

For the existing screens (`/` resume view, profile editor):

- [ ] Page paints on `--paper` background.
- [ ] Body text is `--ink` color, Inter Tight font.
- [ ] Existing `.btn-primary` consumers (e.g. ResumeView download
      button, WorkExperience save button) render ink-filled, not blue.
- [ ] Existing forms still align, accept input, save, and validate as
      before — no layout collapse from the body restyle.
- [ ] No console errors related to fonts or CSS.

For DevTools:

- [ ] Network tab shows requests to `fonts.googleapis.com` (one CSS
      file) and `fonts.gstatic.com` (one font file per family).
- [ ] All requests return 200.
