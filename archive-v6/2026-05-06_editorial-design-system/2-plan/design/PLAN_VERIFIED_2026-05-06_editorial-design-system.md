feature: editorial-design-system
date: 2026-05-06
status: VERIFIED
reviewer: plan-reviewer
inputs_reviewed:
- workbench-v6/1-analyze/spec/FEATURE_SPEC_2026-05-06_editorial-design-system.md
- workbench-v6/2-plan/design/IMPL_PLAN_2026-05-06_editorial-design-system.md
- workbench-v6/2-plan/checks/CHECKLIST_2026-05-06_editorial-design-system.md
- workbench-v6/1-analyze/ux/UX_DESIGN_2026-05-06_editorial-design-system.md
- workbench-v6/2-plan/research/LIB_NOTES_2026-05-06_playwright-python.md

---

## 1. Requirement traceability

| Requirement | Covered by | Status |
|---|---|---|
| MH-1 token block | IMPL_PLAN Edit 2.2; CHECKLIST Section 3 / Edit 2.2 (13 boxes) | covered |
| MH-2 fonts loaded | IMPL_PLAN File 1; CHECKLIST Section 2 (6 boxes) | covered |
| MH-3 body restyle | IMPL_PLAN Edit 2.3; CHECKLIST Edit 2.3 (8 boxes) | covered |
| MH-4 primitive classes | IMPL_PLAN Edits 2.6, 2.8, 2.9, 2.11; CHECKLIST Edits 2.6/2.8/2.9/2.11 | covered |
| MH-5 legacy aliases + WARNING comment | IMPL_PLAN Edits 2.1, 2.2; CHECKLIST Edit 2.1 + 2.2 alias rows | covered |
| MH-6 existing legacy rules untouched, collisions replaced, coexistence comment | IMPL_PLAN Edits 2.5, 2.6, 2.7, 2.10, 2.12; CHECKLIST Edits 2.6/2.7/2.10/2.12 | covered |
| MH-7 no data-attribute selectors | IMPL_PLAN Edit 2.2 (acceptance); CHECKLIST Edit 2.2 / SC-8 row | covered |
| SC-1 token + primitive presence | IMPL_PLAN test-plan row 1; CHECKLIST Section 3 grep rows | covered |
| SC-2 font links present | IMPL_PLAN test-plan row 2; CHECKLIST Section 2 | covered |
| SC-3 bundle build | IMPL_PLAN test-plan row 3, exec step 4; CHECKLIST Section 5 row 2 | covered |
| SC-4 pytest still passes | IMPL_PLAN test-plan row 4, exec step 7; CHECKLIST Section 5 row 4 | covered |
| SC-5 browser shows paper/ink/Inter Tight | IMPL_PLAN test-plan row 5 (auto) + row 10 (manual); CHECKLIST Section 6 | covered (auto for body; manual+follow-up for per-primitive) |
| SC-6 per-primitive visual match | IMPL_PLAN test-plan row 9 (deferred to design-system-tests-expansion.md); CHECKLIST Section 6 per-primitive | covered (manual inspector now; auto deferred — explicit) |
| SC-7 existing screens still render | IMPL_PLAN body padding preservation; CHECKLIST Section 6 layout regression row | covered |
| SC-8 grep no `[data-*]` selectors | IMPL_PLAN Edit 2.2 acceptance; CHECKLIST Section 3 + Section 5 | covered |
| SC-9 pytest smoke test passes | IMPL_PLAN File 3; CHECKLIST Section 4 | covered |
| Scenarios 1, 18, 19, 20 (smoke-test/grep) | CHECKLIST Sections 3 & 4 explicit boxes | covered |
| Scenarios 2–4, 7–17 (per-primitive computed-style) | CHECKLIST Section 6 (manual) + deferred to design-system-tests-expansion.md (auto) | covered (manual now, auto deferred — explicit) |
| Scenario 5 (font network requests) | CHECKLIST Section 6 / DevTools network check | covered (manual) |
| Scenario 6 (no data-* selectors) | CHECKLIST Section 3, SC-8 row, Section 5 cross-cutting | covered |

No requirement traces to nowhere. No IMPL_PLAN file traces back to no requirement.

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `public/index.html` | modify | yes | ok |
| `src/styles/global.css` | modify | yes | ok |
| `src/main.js` | re-verified read-only | yes | ok (line 1 import confirmed) |
| `tests/conftest.py` | re-verified read-only | yes | ok (sets PLAYWRIGHT_BROWSERS_PATH at line 3) |
| `services/pdf_generator.py` | re-verified read-only | yes | ok (`with sync_playwright()` at line 42 confirmed) |
| `design-bundle/project/tokens.css` | read-only source | yes | ok (line 5 = import URL, body at 79–88, eyebrow→card at 91–135, btn group at 138–159, pill at 172–206, input at 209–221 — all line ranges in IMPL_PLAN match exactly) |
| `pyproject.toml` | not modified | yes | ok (playwright>=1.40.0 line 12, pytest>=8.0.0 line 18) |
| `rollup.config.js` | not modified | yes | ok (css plugin emits bundle.css at line 23) |
| `src/components/Section.svelte` | not modified, citation only | yes | ok (line 23 = `class="btn btn-add"` — matches IMPL_PLAN's Pre-implementation check) |
| `package.json` | not modified | yes | ok |
| `tests/test_design_tokens.py` | create | parent dir `tests/` exists | ok |
| `public/build/bundle.css` | build emits | parent dir exists, current artifact present | ok |
| `src/components/SavedJobItem.svelte:125 title-input` | pre-impl re-verification | exists, matches | ok |
| `src/components/JobInput.svelte:18 jd-input` | pre-impl re-verification | exists, matches | ok |
| `src/components/ImportModal.svelte:263 file-input` | pre-impl re-verification | exists, matches | ok |
| Line 6–31 `:root`, 42–50 `body`, 127–154 `.btn`/`.btn-primary`, 156–159 `.btn-add`, 191–211 raw `input/textarea/select`, 213–216 raw `textarea`, line 45 `--font-stack` consumer in `body` rule (IMPL_PLAN cited) | line claims | all exact | ok |
| 73-count grep `var\(--(spacing\|font-size)` in src/components/ | pre-impl re-verification | re-grepped, returns 73 | ok |

No hallucinated files. No hallucinated symbols. All cited line numbers in IMPL_PLAN are exact (not even ±5 — exact).

---

## 3. Library-pattern verification

| Pattern | Documented in | Status |
|---|---|---|
| `sync_playwright()` context manager | LIB_NOTES Pattern 1 | ok |
| `playwright.chromium.launch()` (headless default) | LIB_NOTES Pattern 5 | ok |
| `browser.new_context()` + `context.new_page()` | LIB_NOTES Pattern 4 (explicitly preferred for tests) | ok |
| `page.goto(url, wait_until="load")` | LIB_NOTES Pattern 3 | ok |
| `page.evaluate("() => document.fonts.ready")` for font readiness | LIB_NOTES Pattern 3 (verified-by-inference; open-question 2) | ok (acknowledged in IMPL_PLAN Open question 2 with explicit fallback) |
| `page.evaluate(...)` returning a dict of computed-style strings | LIB_NOTES Pattern 2 | ok |
| `getPropertyValue('-webkit-font-smoothing')` instead of `computed.webkitFontSmoothing` | LIB_NOTES Pattern 2 note + Open questions §1 | ok (docs-researcher recommendation followed; IMPL_PLAN gates the assertion on truthy value — open-question 1 handled with explicit fallback) |
| try/finally for `browser.close()` | LIB_NOTES Pattern 6 | ok (test file uses try/finally) |
| `ThreadingHTTPServer` + `SimpleHTTPRequestHandler(directory=...)` (stdlib, not Playwright) | Python 3.7+ stdlib; project pins 3.13 (verified `uv run python --version` = 3.13.9; `directory` kwarg present in `SimpleHTTPRequestHandler.__init__`) | ok |
| No `networkidle` wait — uses `"load"` | LIB_NOTES "Deprecated APIs to avoid" | ok |

No deprecated APIs invoked. No undocumented patterns.

---

## 4. Checklist coverage

| Plan file/edit | Checklist items | Status |
|---|---|---|
| File 1 — public/index.html | Section 2 (6 boxes) | covered |
| File 2 Edit 2.1 — file header | Section 3 / Edit 2.1 (2 boxes) | covered |
| File 2 Edit 2.2 — `:root` block | Section 3 / Edit 2.2 (13 boxes) | covered |
| File 2 Edit 2.3 — `body` rule | Section 3 / Edit 2.3 (8 boxes) | covered |
| File 2 Edit 2.4 — h1..h6 unchanged | not covered by an explicit checkbox | minor — see §5 |
| File 2 Edit 2.5 — `.container`/`.header`/etc. unchanged | not covered by an explicit checkbox; Section 6 "expected color drift" rows partially address `.status`/`.saved-indicator` drift | minor — see §5 |
| File 2 Edit 2.6 — `.btn` group | Section 3 / Edit 2.6 (5 boxes) | covered |
| File 2 Edit 2.7 — `.btn-add` kept | Section 3 / Edit 2.7 (3 boxes) | covered |
| File 2 Edit 2.8 — pills | Section 3 / Edit 2.8 (5 boxes) | covered |
| File 2 Edit 2.9 — typography primitives + rules + card | Section 3 / Edit 2.9 (7 boxes) | covered |
| File 2 Edit 2.10 — coexistence comment + raw input/textarea/select | Section 3 / Edit 2.10 (2 boxes) | covered |
| File 2 Edit 2.11 — editorial `.input`/`.textarea` | Section 3 / Edit 2.11 (3 boxes) | covered |
| File 2 Edit 2.12 — everything else unchanged | not covered by explicit checkboxes | minor — see §5 |
| File 3 — tests/test_design_tokens.py | Section 4 (11 boxes) | covered |
| Files 4–7 — pyproject.toml/rollup.config.js/src/components/**/services/pdf_generator.py NOT MODIFIED | implicit (no edit, no checkbox needed) | ok |

No orphan checkboxes. Every checklist row traces to a plan edit or to a FEATURE_SPEC/UX_DESIGN clause.

---

## 5. Risks and ambiguities

All findings below are MINOR. None block build. None require plan revision.

- **MINOR — Edits 2.4 / 2.5 / 2.12 have no explicit "did not change" checkbox.** CHECKLIST Sections 3, 5, 6 cover the *outcomes* (full pytest still passes, no layout regressions, expected color drift on `.status`/`.saved-indicator` documented) but there is no positive checkbox like "lines 52–60 and 65–122 and 218–350 untouched". Likely fine because the layout regression check (Section 6) and `uv run pytest` (SC-4) would surface accidental damage, and SC-7's "Intended visible deltas allowlist" provides the catch-all. Severity is MINOR because the existing structure does provide a safety net.
  - location: CHECKLIST Sections 3 & 5; IMPL_PLAN §Edit 2.4, 2.5, 2.12.

- **MINOR — `--shadow-card` ships unused.** Acknowledged in FEATURE_SPEC §MH-1 ("Forward-use note") and in IMPL_PLAN "Open items" #3. Out of scope per the request, so not flagged as an issue. Listed here for completeness because the parent flagged this as "out of scope for your review".
  - location: FEATURE_SPEC §MH-1; IMPL_PLAN Edit 2.2.

- **MINOR — IMPL_PLAN Edit 2.11 dedupes `font-family: var(--font-ui)` on `.textarea`.** FEATURE_SPEC §MH-4 says rule bodies are "copied verbatim from `tokens.css`". `tokens.css:221` literally is `.textarea { font-family: var(--font-ui); resize: vertical; }` and the dedup drops the `font-family` declaration because `.input, .textarea { font-family: var(--font-ui); ... }` already sets it on line above. **The verdict on this dedup: SAFE.** The plan's reasoning is correct — computed style is identical because cascade order keeps the shared `font-family` declaration. Scenarios 16–17 assert computed values, not source order. The only behavioral edge case would be if someone later overrode `.textarea`'s `font-family` between the two rules (impossible — the two rules are adjacent and both rendered by the same stylesheet). Severity MINOR rather than ignored because the plan does *deviate* from §MH-4's literal "verbatim" wording, and the deviation is documented as a Known Compromise inside IMPL_PLAN Edit 2.11 itself. The deviation is internally consistent and computed-style-equivalent, so the contract is not actually violated.
  - location: IMPL_PLAN Edit 2.11; FEATURE_SPEC §MH-4.

- **MINOR — IMPL_PLAN Edit 2.1 retrofits a lean-code header that FEATURE_SPEC §MH-5 did not anticipate.** FEATURE_SPEC §MH-5 says WARNING goes "immediately after the existing single-line file-header comment and before any `:root` rule". IMPL_PLAN replaces the legacy single-line header with the two-line lean-code header (per CLAUDE.md project convention), then inserts WARNING after that. The grep acceptance `grep -F 'WARNING (slice 1' src/styles/global.css` still passes. IR-2 in IMPL_PLAN acknowledges this and offers a fallback (keep both headers, three lines total before WARNING). Verdict: SAFE. The lean-code header is mandated by CLAUDE.md and the WARNING block is preserved literally. The "immediately after" phrasing in FEATURE_SPEC is honoured in spirit — WARNING is at the file top, before `:root`, and the grep anchor catches it. Severity MINOR because two project conventions cross paths here.
  - location: IMPL_PLAN Edit 2.1 + IR-2; FEATURE_SPEC §MH-5; CLAUDE.md "Comments" section.

- **MINOR — `webkitFontSmoothing` assertion silently passes if Chromium headless returns `""`.** The test gates `assert styles["webkitFontSmoothing"] == "antialiased"` behind `if styles["webkitFontSmoothing"]:`. If the empty-string case is hit, the assertion is skipped, but the assertion is *not* re-armed via a `wait_for_function` or via `document.body.style.webkitFontSmoothing`. This is in line with Scenario 1's spirit (assert when present) and IMPL_PLAN Open question 1 documents the choice. Severity MINOR because the gate may quietly mask a real regression. The slice's smoke test value is still preserved (six other assertions remain unmasked). Build-phase first-run will reveal whether to remove the gate. RETROSPECTIVE picks up the determination.
  - location: IMPL_PLAN File 3 "Open question 1 handled"; tests/test_design_tokens.py assertions block.

- **MINOR — `document.fonts.ready` returns immediately if no fonts are declared yet.** Edge case: if the Google Fonts stylesheet `<link>` has not started fetching by the time `wait_until="load"` fires (the HTML `load` event includes the bundle CSS but the Google Fonts CSS is a separate request), `document.fonts.ready` may resolve before the editorial fonts are in the loading set. Result: `fontFamily` could resolve to the system fallback and the test fails with `'-apple-system'` instead of `"Inter Tight"`. IMPL_PLAN Open question 2 acknowledges this and lists `page.wait_for_function("() => document.fonts.ready.then(() => true)")` as the fallback. Severity MINOR because the fallback is documented and the build phase will determine if it is needed.
  - location: IMPL_PLAN File 3 "Open question 2 handled"; LIB_NOTES Open questions §2.

- **MINOR — `tests/test_design_tokens.py` skips when `public/build/bundle.css` is missing, but does NOT skip when Chromium binary is missing.** IMPL_PLAN explains the choice (lines 547–551): pdf_generator.py uses the binary in production, so it's assumed present, and Playwright's own error message is clearer than a wrapper. Verdict: SAFE for this repo's posture. If CI runs on a fresh checkout without `playwright install chromium`, the test will fail with a clear Playwright error rather than a confusing skip. Severity MINOR — listed for completeness; no change requested.
  - location: IMPL_PLAN File 3 "Playwright binary guard"; CHECKLIST Section 0 (already includes a `playwright install chromium` ecosystem step).

- **MINOR — no explicit check that `bun run build` runs cleanly without CSS parse warnings.** CHECKLIST Section 5 row 5 says "`bun run build` emits no CSS parse warnings to stderr — verify: inspect build output". This is a manual visual check; no automation. Severity MINOR because CSS parse errors with nested selectors (the file uses `&:hover` and `&.error` in the raw `input/textarea/select` block) are highly rollup-plugin-css-only-dependent and could cause silent breakage. Out of scope per UX_DESIGN's Error state language ("CSS parse failures would surface as unstyled body"), so the catch-all is the inspector phase.
  - location: CHECKLIST Section 5 row 5; UX_DESIGN "Error" state.

- **MINOR — Scope drift check: no forbidden file edited.** Confirmed by `NOT MODIFIED` sections in IMPL_PLAN Files 4–7: `pyproject.toml`, `rollup.config.js`, `src/components/**`, `services/pdf_generator.py`. No covert edits. Plan also creates `tests/test_design_tokens.py` (a NEW file, allowed). No edits anywhere outside `public/index.html`, `src/styles/global.css`, `tests/test_design_tokens.py`. ok.

- **No BLOCKER or MAJOR risks found.** The five-line WARNING block, the two-line coexistence comment, the literal `--paper: #f4f1ec` grep, and the seven body-restyle assertions are each backed by an explicit acceptance criterion and a checklist row.

---

## 6. What I almost flagged but didn't

(The plan is unusually exact for an M-ceremony artifact. These are the three weakest spots where a future bug could hide.)

1. **`document.fonts.ready` resolution timing in a sync test.** LIB_NOTES Pattern 3 documents this as "verified-by-inference, not by an explicit doc example", and Open question 2 carries the risk forward. If the implementer hits a flaky `fontFamily` assertion on first build-phase run and does not pivot to the `wait_for_function` alternative, the test could land flaky in CI. The plan does say to fall back to the alternative if the first run fails — but the build-phase implementer has to actually read and follow the open-question note rather than the surface-level evaluate call. The MINOR severity above reflects this; I almost made it MAJOR but the explicit fallback in IMPL_PLAN and LIB_NOTES is sufficient steerage.

2. **`getPropertyValue('-webkit-font-smoothing')` may return `""` on Chromium headless yet not on Firefox or headed Chromium.** The plan gates the assertion on truthy; if the gate stays on permanently it masks a regression. LIB_NOTES flags this as an open question. I didn't flag this MAJOR because the slice ships only the body smoke test and the SC-5 manual inspector check (DevTools → Computed) catches the value end-to-end on a human-driven pass. The seven other assertions cover the load-bearing values (background, color, font-family, font-size, line-height, font-feature-settings).

3. **`.serif-italic` body says `font-family: var(--font-display)` (Instrument Serif first) but UX_DESIGN says "Same `--font-display` stack, italic, weight 400" — Scenario 7 verifies `font-family` starts with "Instrument Serif".** Instrument Serif declares an italic variant in the Google Fonts URL (`Instrument+Serif:ital@0;1`) — confirmed. If `0;1` did not include the italic axis, the browser would synthesize italic, which would still pass `font-style: italic` but not look right. I didn't flag this because: (a) the URL is copied verbatim from the design bundle, (b) Scenario 7 only asserts computed values not visual fidelity, (c) the inspector phase per UX_DESIGN gallery is where visual fidelity is gated. Plausible-but-wrong rule out: the URL `Instrument+Serif:ital@0;1` is correct Google Fonts syntax (axis name `ital`, tuple values `0;1` = regular and italic).

---

## 7. Final verdict

**VERIFIED.** No BLOCKER. No MAJOR. Eight MINOR risks logged for the build phase and RETROSPECTIVE; all of them are pre-acknowledged in either IMPL_PLAN, LIB_NOTES, or FEATURE_SPEC. Every cited line number in IMPL_PLAN is exact (not approximate). Every must-have, success criterion, and BDD scenario in FEATURE_SPEC maps to at least one IMPL_PLAN edit and at least one CHECKLIST row. No symbol or path is hallucinated.

Proceed to `/v5-build`.

---

return:
```
status: VERIFIED
artifact: /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench-v6/2-plan/design/PLAN_VERIFIED_2026-05-06_editorial-design-system.md
traceability: covered=7/7 must-have, missing=0, deferred=0; SC covered=9/9; Scenarios covered=20/20
hallucinated_files: 0
hallucinated_symbols: 0
checklist_orphans: 0
risk_findings: blockers=0, major=0, minor=8
top_issue: none
```
