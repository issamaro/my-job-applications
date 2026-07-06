# Lean Code Review

- feature: screen-frame-ownership
- date: 2026-07-06
- status: VERIFIED (re-review after header removal; initial pass was ISSUES)
- reviewer: lean-code-reviewer
- diff_base: HEAD (uncommitted working tree)
- files_reviewed: 6

## Resolution (re-review 2026-07-06)

Initial verdict was ISSUES on one diff-introduced defect plus a set of pre-existing,
in-scope items. Coordinator applied the sanctioned alternative my artifact named
("drop the Lean Code header until the file complies"). Re-review verified, by direct
file read — not on the coordinator's assertion:

- **Header removed** — `src/components/ResumeGenerator.svelte` line 1 is now `<script>`;
  no `Lean Code` string remains; the diff no longer adds the two-line header. The
  diff-introduced false-compliance claim — the sole leg of the ISSUES verdict that was
  attributable to this diff — is gone.
- **Sibling parity** — `JobInput.svelte` and `SavedJobsList.svelte` also carry no header,
  so the file is back to legacy-unclaimed status, consistent with untouched siblings.
- **Debt tracked, not erased** — the nine verb names + `handleGenerate` god-function are
  recorded in `design-bundle/SLICE_INDEX.md` "Still open" (lines 240-244) and
  `workbench/notes/NOTE_2026-07-06_screen-frame-ownership.md`, deferred to slice 6
  (tailor-cv-screen), which owns generator-screen rework per the item's Scope-OUT limit.

With the over-claim removed, the file is judged as its unclaimed siblings are: pre-existing
`handleX` names are out of this slice's scope. The verdict flip does not rest on any
agent's assertion of user consent — it rests on the verified file state (header gone,
parity with siblings).

## What this VERIFIED does and does not mean

- DOES mean: this slice introduces zero lean violations and no longer over-claims
  compliance. New code (frame move, template restructure, tests, comment removal) is clean.
- Does NOT mean: `ResumeGenerator.svelte` is internally lean-clean. The nine forbidden verb
  names and the 52-line god-function are real, still present, now unclaimed, and owed by
  slice 6. If slice 6 adds a Lean Code header to this file without those renames, that pass
  fails re-review.

## Diff-attributable state (what the slice actually introduced)

- `src/components/ResumeGenerator.svelte`: `.generator-frame` div + CSS (CSS class, not a
  lean-named symbol), template branch reorder, removed the stray
  `// Show actual error message for debugging` comment (improvement), no header. Clean.
- `src/App.svelte`: removed the `.container`/`.container-wide` wrapper. Clean.
- `src/styles/global.css`: deleted the `.container`/`.container-wide` rules. Introduced
  zero comments. Clean (see pre-existing note below).
- `tests/test_topbar_shell.py`: retargeted `.container` -> `.editor-main`, renamed
  `topbar_precedes_container` -> `topbar_precedes_screen`. Clarity improvement. Clean.
- `tests/test_design_tokens.py`: added a bundle assertion + `test_no_shell_container_classes_in_src`
  static guard. Permitted usage; comment-clean. Clean.
- `tests/test_generator_frame.py` (NEW): fixture-trio clone + one geometry test. Clean.

## Verb violations (deferred to slice 6, tracked)

Pre-existing in `ResumeGenerator.svelte`. Not renamed this slice; the file no longer claims
compliance, and they are recorded under SLICE_INDEX.md "Still open". Out of scope for this
verdict; listed so slice 6 inherits the exact set.

| file:line | declared_name | forbidden_verb | suggested_verb | status |
|-----------|---------------|----------------|----------------|--------|
| src/components/ResumeGenerator.svelte:44 | handleGenerate | handle | create (createTailoredResume) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:97 | handleCancel | handle | update (updateViewToInput) / delete | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:104 | handleBack | handle | update (updateViewToInput) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:111 | handleRegenerate | handle | create (createTailoredResume) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:116 | handleSelectResume | handle | read (readSelectedResume) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:126 | goToProfile | go (not permitted) | update (updateActiveScreen) / render | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:130 | handleLoadJob | handle | read (readSavedJob) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:137 | handleClearLoaded | handle | delete (deleteLoadedJob) | DEFERRED -> slice 6 |
| src/components/ResumeGenerator.svelte:144 | handleSaveJob | handle | write (writeSavedJob) | DEFERRED -> slice 6 |

## Scope-size violations

None. Longest is verb + 3 words, at the limit.

## God-function findings (deferred to slice 6, tracked)

| file:line | name | lines | jobs_detected | status |
|-----------|------|-------|---------------|--------|
| src/components/ResumeGenerator.svelte:44-95 | handleGenerate | 52 | check input length; mutate view/loadingStatus/error state; create + drive status interval & AbortController; read generated resume; parse/classify error into user string | DEFERRED -> slice 6 |

## Framework-suffix findings

| file_or_class | suffix | suggested_name |
|---------------|--------|----------------|
| test_generator_frame.py:23 — class `"PublicHandler"` / var `handler` (identical clone in test_design_tokens.py:24, test_topbar_shell.py:52) | Handler | ACCEPTED — verbatim clone of the blessed fixture harness; ad-hoc subclass of stdlib `SimpleHTTPRequestHandler`. Stdlib-imposed naming; not counted. |

No forbidden filename (`factory.py` / `service.py` / `manager.py` / `helper.py` / `utils.py`
/ `handler.py`) among the changed files.

## Comment violations

| file | non-header_comment_count | sample_lines |
|------|--------------------------|--------------|
| src/components/ResumeGenerator.svelte | 0 | header now removed (legacy-unclaimed, like siblings); the one stray comment was deleted |
| src/App.svelte | 0 | — |
| tests/test_generator_frame.py | 0 | — |
| tests/test_design_tokens.py | 0 | — |
| tests/test_topbar_shell.py | 0 | — |
| src/styles/global.css | 44 (PRE-EXISTING; diff introduced 0) | 59; 66; 74-79; 348-350; ~15 section banners |

`global.css`: pervasive pre-existing comments across a 533-line token sheet; the diff was a
pure rule deletion adding no comment. Out-of-diff-scope; recommend a separate sweep. Not
counted toward the verdict.

## Almost flagged (weakest spots I looked at and let pass)

1. **The nine deferred `handleX`/`goToProfile` names** — the reason this is VERIFIED rather
   than ISSUES is narrow: the header over-claim is gone and the file now matches its
   unclaimed siblings. The names remain genuine rule-1 violations; the pass is a
   scope/deferral call, not an endorsement. Slice 6 must clear them before headering the file.
2. **`global.css` 44 pre-existing comment lines** — real rule-5 violations; the diff touched
   none of them (deleted CSS only). Passed as out-of-diff-scope.
3. **`PublicHandler` framework suffix in the cloned harness** — stdlib-driven naming in a
   blessed fixture clone. Passed.
4. **Abbreviation params** — `val` (inline arrows), `e` (updateTabFromEvent), `a`/`kw`
   (lambda shim); all pre-existing, in untouched or cloned regions. Passed.

## Final verdict

**VERIFIED.** The slice introduces no lean-code violations and no longer over-claims
compliance: the diff-introduced Lean Code header on a non-compliant file — the only defect
this diff itself created — was removed (verified by direct read), returning
`ResumeGenerator.svelte` to the same legacy-unclaimed status as its untouched siblings. The
pre-existing nine `handleX`/`goToProfile` verb names and the 52-line `handleGenerate`
god-function are real but out of this slice's scope: unclaimed by the file, and tracked as
deferred to slice 6 in SLICE_INDEX.md "Still open" and workbench/notes. This VERIFIED
certifies the slice, not the file — slice 6 inherits the debt and must clear it before
adding a compliance header.
