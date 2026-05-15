# RETROSPECTIVE — editorial-design-system

**Date:** 2026-05-06
**Slug:** editorial-design-system
**Ceremony level:** M
**Slice:** 1 of 9 (foundation) in the editorial redesign initiative

## What landed

- `public/index.html`: three Google Fonts `<link>` tags inserted before bundle.css link.
- `src/styles/global.css`: full rewrite of header + `:root` + body + buttons + pills + typography primitives + editorial inputs; legacy aliases kept for unrestyled components.
- `tests/test_design_tokens.py`: created. Single smoke test asserts seven body computed-style values via sync Playwright.
- 246/246 pytest pass (no regressions). `bun run build` clean. All Section 1–5 grep gates pass.

## Surprises encountered during build

- None. The plan was exact enough that the implementation was a transcription with no judgment-call moments. Every grep acceptance check returned what IMPL_PLAN predicted, on the first try.

## Open items — resolution

1. **`webkitFontSmoothing` headless readability** — RESOLVED (gate held). Test passed with the truthy-gate left in place. Headless Chromium did return the value successfully (the gate did not have to silently skip it on this run). On the strength of one passing run, do not yet remove the gate — keep it as defensive coding because the spec note flagged a real Chromium quirk. Re-evaluate on the next CSS slice if the assertion has not fired truthy in CI.
2. **`document.fonts.ready` resolution timing** — RESOLVED. `page.goto(..., wait_until="load")` followed by `page.evaluate("() => document.fonts.ready")` was sufficient; the fallback `page.wait_for_function` form was not needed. `fontFamily.startswith('"Inter Tight"')` asserted truthy on first attempt.
3. **`--shadow-card` unused** — Acknowledged. Will be consumed by slices 7 & 8 per FEATURE_SPEC. No action.
4. **`--color-error → --accent` discoverability** — WARNING block in `global.css` is the breadcrumb. Per-slice migration planned in slices 2–9.
5. **`:focus-visible` outline** — Deferred to slice 2 (topbar-shell) per UX_DESIGN. No action this slice.

## What was harder than expected

- Nothing was harder than expected. The plan reviewer's "unusually exact for an M-ceremony artifact" finding held up: the implementation was mechanical.

## What was easier than expected

- The legacy-alias contract: zero component edits, zero downstream churn. The `--color-primary: var(--accent)` etc. lines did all the work — every existing screen kept rendering with no broken layouts.

## What the next similar slice should do differently

- The lean-code two-line file header retrofit (Edit 2.1) caused a tiny FEATURE_SPEC↔IMPL_PLAN tension (resolved in IR-2). Future CSS slices should retrofit lean-code headers in the same slice that owns the file, not a separate pass — and the FEATURE_SPEC author should anticipate the project header convention so the WARNING block placement doesn't require an IR follow-up.
- The `.textarea` font-family dedup in Edit 2.11 deviated from FEATURE_SPEC §MH-4's "verbatim" wording. The deviation was correct (computed-style equivalent), and the plan-reviewer accepted it, but next slice's FEATURE_SPEC should phrase rule-body copies as "computed-style equivalent" not "verbatim" — gives the implementer room to dedup without a contract-violation flag.
- Per-primitive computed-style assertions were deferred to `design-system-tests-expansion.md`. That backlog item is already refined and sequenced after slice 2. Build it before slice 3 so slices 3–9 inherit visual regression coverage rather than relying on per-slice inspector passes.

## Add to project-checks.md? (no file exists today)

If we ever introduce `project-checks.md`, add:
- CSS edits ship with their own automated computed-style smoke test (sync Playwright + ThreadingHTTPServer pattern from this slice — copy as the template).
- Legacy color aliases mapping onto new tokens must be accompanied by a WARNING comment naming the slice that introduced the mapping. Grep gate: `grep -F 'WARNING (slice' src/styles/global.css`.
- Any new `[data-*]` attribute selector inside `src/styles/global.css` requires explicit justification — current default is zero.

## Inspector phase (deferred to user)

Automated coverage (greps + 246/246 pytest + body smoke test) satisfies SC-1, SC-3, SC-4, SC-8, SC-9 and BDD Scenarios 1, 18, 19, 20. SC-5, SC-6, SC-7 require a browser session — bundled into the `INSPECTION_RESULTS_2026-05-06_editorial-design-system.md` payload and runnable via `uv run uvicorn main:app --reload`. Per IMPL_PLAN, per-primitive auto-coverage is the job of `design-system-tests-expansion.md` after slice 2.
