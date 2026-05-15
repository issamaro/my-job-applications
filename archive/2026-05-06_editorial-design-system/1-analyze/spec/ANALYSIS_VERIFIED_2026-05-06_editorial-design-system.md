# ANALYSIS_VERIFIED — editorial-design-system

**Date:** 2026-05-06
**Slug:** editorial-design-system
**Status:** VERIFIED

## Summary

Adversarial review run #2 (after edits). All 8 prior findings closed.
Phase 1 gate passed; proceed to Phase 2 (Plan).

```
status: VERIFIED
bdd: testable=20/20, untestable=0
vague_terms: 0
ux_states_missing: 0
traceability: covered=7/7, missing=0
risk_findings: blockers=0, major=0, minor=0
```

## Findings closure (run #1 → run #2)

| # | Severity | Resolution location | Status |
|---|----------|---------------------|--------|
| 1 | BLOCKER | FEATURE_SPEC §MH-1: five legacy non-color tokens listed with values; grep-count justification | CLOSED |
| 2 | MAJOR | FEATURE_SPEC §MH-6: exact grep command + outputs cited; build-phase re-run instruction | CLOSED |
| 3 | MAJOR | FEATURE_SPEC §MH-5 "Known compromise" + literal `WARNING (slice 1` block; R-3 references; Scenario 18 asserts grep | CLOSED |
| 4 | MAJOR | UX_DESIGN "Intended visible deltas" block with five enumerated changes + specific component paths; SC-7 references allowlist | CLOSED |
| 5 | BDD-gap | Scenario 1 expanded; Scenarios 7–17 per primitive; 18–19 literal comment greps; 20 smoke-test contract | CLOSED |
| 6 | MINOR | UX_DESIGN Tracking paragraph + SLICE_INDEX "Known compromises carried by slice 1" section | CLOSED |
| 7 | MINOR | FEATURE_SPEC §MH-1 "Forward-use note" for `--shadow-card` (slices 7, 8) | CLOSED |
| 8 | MINOR | FEATURE_SPEC R-2 cites literal `Note: the rules below` comment; Scenario 19 asserts grep | CLOSED |

## New content validated

- SC-3 uses `bun run build`.
- SC-4 uses `uv run pytest`.
- SC-9 covers smoke test `tests/test_design_tokens.py`.
- Follow-up backlog item `backlog/refined/design-system-tests-expansion.md`
  uses `uv run pytest` + `bun run build`; explicit no-npm/no-pip
  guardrails; sequencing (after slice 2, before slice 3) is principled.

## Reviewer's cosmetic notes (not gate failures)

1. UX_DESIGN line 176–177 referenced `npm run build` in deferred-state
   narrative copy. **Fixed inline** after the verification — replaced
   with `bun run build`.
2. Scenario 1's `webkitFontSmoothing` assertion is WebKit/Chromium
   specific; Playwright Python defaults to Chromium so the smoke
   test works in practice. Cross-browser coverage is explicitly
   deferred in the follow-up backlog Scope OUT.
3. The "Kept verbatim" list in MH-6 (25+ legacy class names) was not
   exhaustively grep-checked against `src/components/`; SC-7 +
   last-defined-wins rule are the safety net during build.

## Outcome

VERIFIED. Proceed to Phase 2 (Plan).
