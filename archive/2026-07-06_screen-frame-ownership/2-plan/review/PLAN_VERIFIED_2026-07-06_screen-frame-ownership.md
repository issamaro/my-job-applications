---
feature: screen-frame-ownership
date: 2026-07-06
status: VERIFIED
reviewer: plan-reviewer
inputs_reviewed:
  - backlog/refined/screen-frame-ownership.md (FEATURE_SPEC equivalent, ceremony S)
  - workbench/2-plan/design/IMPL_PLAN_2026-07-06_screen-frame-ownership.md
  - workbench/2-plan/checklist/CHECKLIST_2026-07-06_screen-frame-ownership.md
  - design-bundle/SLICE_INDEX.md (shared initiative context)
  - LIBRARY_NOTES: none (S ceremony — in-repo pattern verification substituted)
  - UX_DESIGN: none (S ceremony)
review_rounds:
  - "round 1: ISSUES (1 MAJOR resume-preview false-green, 1 MINOR rename ambiguity)"
  - "round 2 (delta): both resolved and empirically verified → VERIFIED"
---

# Plan review — screen-frame-ownership

Verdict: **VERIFIED** after a two-round review. Round 1 raised 1 MAJOR + 1 MINOR;
both are fixed and I re-verified the delta (not a full re-review, per the coordinator).
Zero hallucinated files, zero hallucinated symbols; every path, line, and symbol resolves.

## Round-2 delta verification (2026-07-06)

### MAJOR-1 — RESOLVED (resume-preview coverage + regex correctness)
The plan now (a) splits criterion C3 into two traceability rows and two CHECKLIST
items (editor-column vs resume-preview), (b) strikes the nonexistent "slice-4 suite"
phrase from the Test plan, and (c) adds an automated bundle-text assertion appended
to `test_bundle_carries_consolidation_rules` (test_design_tokens.py:84, `css` in scope
at :88, `re` imported at :4) for the resume-preview half, with rendered-geometry
judgment routed to a Phase-3 inspector visual bullet.

The regex was itself broken in the first-draft fix (`\.resume-preview\s*\{…`) and I
caught it: the built bundle scopes the selector as `.resume-preview.svelte-kyrtaa {`
(public/build/bundle.css:2085-2086), so a `\s*` gap cannot cross the injected
`.svelte-kyrtaa` class. The coordinator corrected it to `[^{]*`. I re-ran the CURRENT
pattern `\.resume-preview[^{]*\{[^}]*padding:\s*var\(--d-pad\)` against the real bundle
with `re` (no plan code executed):

| check | result |
|---|---|
| matches the real bundle | True — anchored on the padding rule (`.resume-preview.svelte-kyrtaa {\n padding: var(--d-pad)`) |
| matches focus-visible group rule alone (no padding in body) | False — no false positive; `[^}]*` can't cross `}` to borrow padding from a sibling rule |
| matches when focus-visible rule precedes the padding rule | True — still finds the padding rule |
| matches after `padding: var(--d-pad)` is removed | False — the assertion has real teeth |

The `[^{]*`/`[^}]*` classes are brace-bounded, so each match is confined to one rule
block; the pattern is also robust to rebuild hash churn (it never hardcodes `kyrtaa`).

### MINOR-1 — RESOLVED (topbar rename)
Section 4 now reads "rename `topbar_precedes_container` → `topbar_precedes_screen` at
BOTH sites (assignment line 105 and assert line 122)" and the self-contradictory
"keep the assert" phrasing is gone (now "keep the DOCUMENT_POSITION_FOLLOWING logic").

## 1. Requirement traceability (refined "Success criteria" as must-haves)

| requirement | covered_by | status |
|---|---|---|
| C1 grep container-wide/`.container` = 0 | static guard `test_no_shell_container_classes_in_src` + ship grep (CHECKLIST 2,3) | covered |
| C2 Tailor CV form centered ≤ 800px @1512×860 | `test_generator_input_frame_geometry` (CHECKLIST 5,6,7) | covered |
| C3a `.editor-column` 940px unchanged | existing `test_editorial_page_frame` (test_profile_editor_restyle.py:110) | covered |
| C3b `.resume-preview` `--d-pad` unchanged | bundle-text assertion in `test_bundle_carries_consolidation_rules` (verified matches) + Phase-3 inspector visual bullet | covered (honest split — no computed-style probe; see almost-flagged #1) |
| C4 static guard passes | `test_no_shell_container_classes_in_src` | covered |
| C5 `test_generator_frame.py` passes | same file | covered |
| C6 full pytest green incl. retargeted topbar | test-runner | covered |
| C7 SLICE_INDEX contract line | ship-phase ledger sweep (manual — file gitignored) | covered (manual only; unavoidable) |

No false-green rows remain. No IMPL_PLAN file traces to a non-requirement (no scope creep).

## 2. File-path & symbol verification (anti-hallucination) — unchanged from round 1, all OK

Verified present: App.svelte:26 (`.container` div w/ `class:container-wide`, only two tabs
`profile`/`resume`, both trigger container-wide → `.container` 800px is inert today);
global.css:175-179/181-184 (rules), :63 (`--spacing-section:24px`), :147 (`box-sizing:border-box`,
universal); ResumeGenerator.svelte 4-branch chain (169-234), `view='input'`(9)/`profileIncomplete=false`(16)/`checkProfile` try-catch (32-39);
test_topbar_shell.py `test_topbar_renders_at_top`(98)/`create_loaded_page`(72)/`public_url`(63)/`topbar_precedes_container`+`querySelector('.container')`+`DOCUMENT_POSITION_FOLLOWING`(105-122);
ProfileEditor.svelte:53 `<main class="editor-main">` (top-level); test_disabled_slots_inert(168) sees `.profile-header`;
ResumeView.svelte `.resume-preview`(419)/`padding:var(--d-pad)`(811); test_editorial_page_frame(74) asserts 940px(110);
fixture trio test_design_tokens.py:17/23/36; test_no_legacy_color_tokens_in_components test_profile_editor_restyle.py:282;
photo-upload-container PhotoUpload.svelte:124/210; progress-container ProgressBar.svelte:5/13;
`[data-slot-id="tailor"]` Topbar.svelte:14 (id→tab 'resume'); test_click_tailor_routes:207; main.js:6 mount body;
test_generator_frame.py absent (correct — create target, parent tests/ exists).

hallucinated_files: 0 · hallucinated_symbols: 0

## 3. In-repo pattern verification (substitutes for LIBRARY_NOTES at S)

Fixture trio (test_design_tokens.py:17-42, per-file convention — conftest.py has only
`setup_test_db`/`client`, so cloning is correct); static-guard grep pattern
(test_no_legacy_color_tokens_in_components:282); geometry-assertion pattern
(test_editorial_page_frame:74); no-mock stance (test_click_tailor_routes:207 +
verified `checkProfile` catch leaves `profileIncomplete=false`). All OK.

### Static-guard regex (`(?<![\w-])container(?:-wide)?(?![\w-])`)
Traced against all 7 real `container` occurrences: correctly skips the two hyphen-preceded
cousins (photo-upload-container, progress-container), catches `class="container"`,
`class:container-wide`, `.container {`, `querySelector('.container')`. After the three
deletions only the two cousins remain in `src/` → guard passes on first run. `src/` holds
only svelte/js/css, so the guard's suffix filter has no coverage gap vs. the C1 all-files grep.

## 4. Checklist coverage

Every IMPL_PLAN file has ≥1 checklist item (App.svelte→1,2,3,4; global.css→2,3;
ResumeGenerator→1,5,6,7; test_topbar_shell→4; test_design_tokens→2 + resume-preview
bundle item; test_generator_frame→5,6,7; SLICE_INDEX→10). total_checkboxes=14 (was 13;
+1 from the C3 split). checklist_orphans: 0. Ecosystem items verified (.python-version=3.13,
requires-python>=3.13, playwright>=1.40.0, pytest>=8.0.0, pytest-asyncio>=0.24.0).

## 5. Risks & ambiguities

Both round-1 findings resolved (see Round-2 delta). No open BLOCKER/MAJOR/MINOR.
SLICE_INDEX amendment is additive (no contradiction with shared decisions); consuming
`--spacing-section` is safe (survives until after slice 9, frame dies at slice 6); no
sibling refined item references App.svelte/`.container` (the lone "containers" hit in
interview-prep-screen.md:34 is generic English); no ledger deferral names this item.

## What I almost flagged but didn't

1. **The resume-preview bundle assertion is orthogonal to this feature's actual risk.**
   It proves the `.resume-preview{padding:var(--d-pad)}` rule is *compiled into* the
   bundle — but this feature never touches ResumeView.svelte, so that rule can't regress
   from these changes; the assertion is a standing invariant, not a guard against the
   shell edit. It also proves rule *presence*, not that the rule *wins at runtime*
   (specificity/override/element-present are untested). Real confidence for C3b rests on
   (a) the structural argument that `.resume-preview`'s ancestor goes from `.container-wide`
   (max-width:none;padding:0) to `.resume-generator` (padding:0) — an equivalent context —
   and (b) the Phase-3 inspector visual bullet, a human step, not an automated gate. Not
   flagged as a defect because the plan is explicit about this ("no computed-style test…
   a probe would need a full generate round-trip for a screen this change never touches")
   and the residual risk is near-zero; adding a computed-style test would be disproportionate.
2. **C7 (SLICE_INDEX contract line) has no automated verification** — `design-bundle/` is
   gitignored, so no git-tracked test can assert it; it relies on a manual ship-phase
   ledger sweep. Unavoidable given the gitignore, and the "applied now, not committed"
   convention is owned explicitly by both the refined item and the plan.
3. **Body-level reset not re-verified.** After outdenting the `{#if}` chain, screens become
   direct `<body>` children; I did not read `body`'s own margin/padding. Left unflagged
   because `.container-wide` already makes screens edge-flush against the same body today,
   so post-change parity holds regardless of the body reset value.

## Final verdict

**VERIFIED** — no BLOCKER, no MAJOR, no MINOR. Both round-1 findings are fixed; the
corrected bundle-text regex is empirically confirmed to match the real bundle, avoid the
focus-visible false positive, and fail if the padding rule disappears. The plan may proceed
to /v5-build. Carry almost-flagged #1 into the Phase-3 inspector pass (the resume-preview
rendered-geometry check is a human bullet, not an automated gate).
