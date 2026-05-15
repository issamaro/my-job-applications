feature: editorial-design-system
date: 2026-05-06
status: READY
playwright: skipped

---

## Playwright

Skipped — no dev server running at inspection time. The automated test
`tests/test_design_tokens.py` already passed (SC-9 / Scenario 1 covered).
To run a full Playwright smoke: `uv run uvicorn main:app --reload`, then
`uv run pytest tests/test_design_tokens.py`.

---

## Color-drift allowlist (document, do not fail)

Three tokens changed from legacy values. The inspector must treat these as
intended, not regressions:

- `.status` / `.saved-indicator` — editorial green `rgb(74, 107, 58)` replaces
  legacy `#008800`. Darker, warmer.
- `.delete-link` / `.error-message` — terracotta `rgb(184, 68, 42)` replaces
  legacy red. Same token as primary CTA (`--accent`). WARNING comment in
  `global.css` documents this.
- `.form-error` background — light terracotta tint `rgba(184,68,42,0.05)`,
  not light red. Visually similar warmth, different hue.

---

## Manual checklist

### A — Page-level body restyle

- [ ] Start the app: `uv run uvicorn main:app --reload`, open http://localhost:8000/. Confirm page background is paper — DevTools Computed → background-color = `rgb(244, 241, 236)`, NOT white `rgb(255,255,255)`.
- [ ] DevTools Computed on `<body>` → color = `rgb(26, 24, 20)` (ink, not the old `rgb(26,26,26)`).
- [ ] DevTools Computed on `<body>` → font-family starts with `"Inter Tight"`.
- [ ] DevTools Computed on `<body>` → font-size = `14px`, line-height = `21px` (1.5 × 14).

### B — Buttons and primary CTAs

- [ ] ResumeView Download button (at `/`): background is ink `rgb(26, 24, 20)`, NOT blue `rgb(0,102,204)`.
- [ ] WorkExperience Save buttons (×2) and Education Save buttons (×2): same ink fill, not blue.
- [ ] Skills Add button and ResumeGenerator primary buttons: same ink fill.
- [ ] Hover any `.btn` (base variant): background shifts to `--paper-2` and border shifts to `--ink-3` within ~150ms.

### C — Form inputs and focus rings

- [ ] Click any `<input>` in the profile editor: border swaps to ink `rgb(26, 24, 20)` and no browser default outline is visible (outline: none in effect).
- [ ] Click a `.textarea` in the profile editor: same border swap as `.input`, and the field is vertically resizable.
- [ ] Focus ring color is terracotta `rgb(184, 68, 42)` on legacy raw `<input>` / `<textarea>` — NOT blue. (These use `var(--color-primary)` which now aliases to `--accent`.)

### D — Typography primitives (DevTools or scratch injection)

- [ ] Inject `<span class="eyebrow">Test</span>` via DevTools "Edit as HTML" → font-family starts with `"JetBrains Mono"`, text-transform = `uppercase`, letter-spacing = `0.12em`, color = `rgb(107, 99, 88)`.
- [ ] Inject `<span class="display">Test</span>` → font-family starts with `"Instrument Serif"`, letter-spacing = `-0.01em`.
- [ ] Inject `<span class="serif-italic">Test</span>` → font-family starts with `"Instrument Serif"`, font-style = `italic`.
- [ ] Inject `<span class="num">42</span>` → font-family starts with `"JetBrains Mono"`, font-variant-numeric includes `tabular-nums`.

### E — Rules, card, and pill primitives

- [ ] Inject `<hr class="rule">` → exactly 1px tall, border-top color `rgb(200, 191, 177)`, margin = `0`.
- [ ] Inject `<hr class="rule-soft">` → border-top color `rgb(221, 213, 199)`.
- [ ] Inject `<div class="card">X</div>` → background `rgb(251, 250, 246)`, border `1px solid rgb(200, 191, 177)`, border-radius `4px`.
- [ ] Inject `<span class="pill">X</span>` → border-radius `999px`, font-size `10px`, text-transform `uppercase`, letter-spacing `0.06em`, color `rgb(107, 99, 88)`.
- [ ] Inject `<span class="pill-accent">X</span>` → color `rgb(184, 68, 42)`, background `rgb(233, 200, 189)`, border-color `rgb(184, 68, 42)`.
- [ ] Inject `<span class="pill-positive">X</span>` → color `rgb(74, 107, 58)`, background `rgb(214, 222, 201)`, border-color `rgb(74, 107, 58)`.
- [ ] Inject `<span class="pill-warn">X</span>` → color `rgb(160, 112, 36)`, background `rgb(234, 216, 182)`, border-color `rgb(160, 112, 36)`.
- [ ] Inject `<span class="pill-solid">X</span>` → background `rgb(26, 24, 20)`, color `rgb(244, 241, 236)`.

### F — Network and font loading

- [ ] DevTools Network → filter `googleapis` → one CSS stylesheet request returns 200.
- [ ] DevTools Network → filter `gstatic` → four font file requests return 200 (one per family: Fraunces, Instrument Serif, Inter Tight, JetBrains Mono).
- [ ] DevTools Console → zero errors related to fonts or CSS.
- [ ] Block `fonts.googleapis.com` in DevTools (Network → Request blocking), reload → every page element remains legible with fallback fonts (no FOIT, no collapsed layout).

---

## Decisions

none — parent collects user verdict
