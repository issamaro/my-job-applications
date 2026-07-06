feature: screen-frame-ownership
date: 2026-07-06
total_checkboxes: 14
derived_from: IMPL_PLAN_2026-07-06_screen-frame-ownership.md, screen-frame-ownership.md, .python-version, pyproject.toml

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13`
  (verify: `cat .python-version`)
  → source: `.python-version` (repo file, read during discovery)

- [ ] Runtime version pinned: `pyproject.toml` `requires-python = ">=3.13"`
  (verify: `cat pyproject.toml`)
  → source: `pyproject.toml` "[project]" block, `requires-python` line

- [ ] Virtual environment created and activated, matching the `dev` dependency
  group (`pytest>=8.0.0`, `pytest-asyncio>=0.24.0`, `playwright>=1.40.0`)
  (verify: `uv venv && uv sync` or equivalent, then `python -c "import pytest, playwright"`)
  → source: `pyproject.toml` "[dependency-groups] dev" block

## Section 1 — Dependencies

n/a — no source. No LIBRARY_NOTES were produced for this feature; IMPL_PLAN
states every change clones an in-repo pattern (ceremony S, no research
phase, no new libraries introduced).

## Section 2 — Syntax

n/a — no source. Section 2 is derived from LIBRARY_NOTES-documented library
patterns; none exist for this feature. The IMPL_PLAN's "clone this pattern"
references (Playwright fixture trio, static-guard shape) point at in-repo
test files, not library documentation, so they are captured as Section 4
test items instead of invented Syntax entries here.

## Section 3 — UX

n/a — no source. No UX_DESIGN document was produced (S ceremony,
frame-geometry-only change per the caller's brief).

## Section 4 — Tests

- [ ] Bundle rebuilt via `bun run build` after the three source edits
  (`App.svelte`, `global.css`, `ResumeGenerator.svelte`) and before any
  Playwright test run
  → source: IMPL_PLAN "Build order" section ("1 → 2 → 3 (source), rebuild
  bundle (`bun run build`), then 4 → 5 → 6 (tests)...Rebuild before
  test-runner or every Playwright test goes stale against the old bundle.")

- [ ] Static guard `test_no_shell_container_classes_in_src` created in
  `tests/test_design_tokens.py`, scanning `src/**/*.{svelte,js,css}` with
  the boundary regex `(?<![\w-])container(?:-wide)?(?![\w-])`, asserting
  `offenders == {}`
  → source: IMPL_PLAN section "5. `tests/test_design_tokens.py` — modify
  (static guard home)"

- [ ] `grep -rn "container-wide" src/` returns zero matches; `grep -n
  '\.container' src/styles/global.css` returns zero matches (ship-time
  spot-check, independent of the automated guard)
  → source: backlog/refined/screen-frame-ownership.md "Success criteria"
  bullet 1; IMPL_PLAN "Success criteria traceability" table row 1

- [ ] `test_topbar_renders_at_top` (in `tests/test_topbar_shell.py`)
  retargeted: waits for `.editor-main` after `create_loaded_page`,
  assertion renamed `topbar_precedes_container` → `topbar_precedes_screen`,
  `querySelector('.container')` retargeted to `.editor-main`, existing
  `DOCUMENT_POSITION_FOLLOWING` logic and assert kept unchanged
  → source: IMPL_PLAN section "4. `tests/test_topbar_shell.py` — modify"

- [ ] Unit test covers BDD scenario "Tailor CV job-description form renders
  as a centered column no wider than 800px with visible margins on both
  sides, at 1512×860, before generating a resume" at
  `tests/test_generator_frame.py::test_generator_input_frame_geometry`
  → source: backlog/refined/screen-frame-ownership.md "Sketch of BDD
  scenarios" bullet 1; IMPL_PLAN section "6. `tests/test_generator_frame.py`
  — create"

- [ ] `test_generator_input_frame_geometry` asserts computed `maxWidth` of
  `.generator-frame` equals `"800px"`
  → source: IMPL_PLAN section 6, "computed `maxWidth` of `.generator-frame`
  == `"800px"`"

- [ ] `test_generator_input_frame_geometry` asserts centering via
  `getBoundingClientRect` (`left > 0`, `right < innerWidth`,
  `|left - (innerWidth - right)| <= 1`)
  → source: IMPL_PLAN section 6, "`getBoundingClientRect`: `left > 0`,
  `right < innerWidth`, and `|left - (innerWidth - right)| <= 1`"

- [ ] BDD scenario 2, profile half: `.editor-column` still caps at 940px via
  existing `test_editorial_page_frame`, run as regression
  → source: backlog/refined/screen-frame-ownership.md "Sketch of BDD
  scenarios" bullet 2; IMPL_PLAN "Test plan" section, "Regression:" bullet

- [ ] BDD scenario 2, resume-preview half: bundle-text assertion appended to
  `test_bundle_carries_consolidation_rules` — built `bundle.css` still carries
  `padding: var(--d-pad)` inside the `.resume-preview` rule
  (`re.search(r"\.resume-preview[^{]*\{[^}]*padding:\s*var\(--d-pad\)", css)` —
  `[^{]*` tolerates the Svelte scoping hash, e.g. `.resume-preview.svelte-kyrtaa`);
  rendered-geometry judgment goes to an inspector visual bullet, not a
  computed-style test
  → source: IMPL_PLAN section 5 (bundle-text assertion) + "Success criteria
  traceability" row for `.resume-preview`; plan-review fix 2026-07-06

- [ ] Full pytest suite passes, including the retargeted
  `tests/test_topbar_shell.py`
  → source: IMPL_PLAN "Success criteria traceability" table row "full suite
  green incl. retargeted topbar test | test-runner"

- [ ] `design-bundle/SLICE_INDEX.md` "Shared decisions (fixed across all
  slices)" section carries the "Screens self-frame (2026-07-06,
  screen-frame-ownership)" contract line
  → source: IMPL_PLAN section "7. `design-bundle/SLICE_INDEX.md` — modify";
  "Success criteria traceability" table row "SLICE_INDEX carries the
  contract line | ship-phase ledger sweep"

## Section 5 — Accessibility

n/a — no source. No UX_DESIGN document exists for this feature; there is
no accessibility section to derive checks from.
