# RETROSPECTIVE — llm-call-breadcrumbs

**Slug:** llm-call-breadcrumbs
**Date:** 2026-05-27
**Ceremony:** M
**Outcome:** 273 tests pass (was 262 pre-feature); 11 new tests added net; zero failures.

---

## What surprised

- **`test_pdf_api.py` had ONE `mock_llm.return_value` line, not 8.** The plan
  said 8 occurrences across the file; the actual codebase uses a single shared
  `_generate_resume(client, mock_llm)` helper that sets the return-value once
  and is fed by 8 `@patch` decorators. The mechanical sweep collapsed to a
  single edit. Plan was based on grep-by-decorator-count, not by
  assignment-count. Future plans against this codebase should grep both.

- **The mock sweep transformer scripted itself out of correctness.** The
  ad-hoc Python script that wrapped `mock_llm.return_value = {...}` with
  `create_llm_result(...)` over-matched the closing brace, producing `}})`
  instead of `})` on every conversion. Caught by the parse check before
  the test run, but added a fix-up pass. Lesson: prefer libcst/ast over
  regex when transforming Python at scale.

- **The Gemini SDK `usage_metadata` has 11 sub-fields, not 2.** `LIBRARY_NOTES`
  flagged `prompt_token_count` and `candidates_token_count` as the relevant
  ones, and the live `vars(...)` check confirmed both spellings are present
  AND there are 9 other token-related fields (`cached_content_token_count`,
  `thoughts_token_count`, `tool_use_prompt_token_count`, etc.). Out of
  scope for this slice, but the field set is richer than expected — could
  be useful for future cost/quality analysis.

- **Lean-code reviewer caught 5 abbreviations and 2 disallowed verbs in
  one shot.** Without the review pass, `t0`, `snap`, `r1`/`r2`, `cols`,
  `_count_resume_rows`, `capture_and_return` would all have shipped.
  These felt natural-Pythonic; the rule against abbreviations is the most
  common drift point.

---

## What was harder than expected

- **The four database.py sync locations.** Adding 9 columns required
  edits at lines 339-353 (inline DDL), 357-376 (migrations list), 207-222
  (recreate CREATE), and 228-236 (recreate INSERT/SELECT) — four
  near-identical sections that must agree on column count and order. The
  CHECKLIST broke each into its own checkbox, which mattered. Without it
  the recreate path would have shipped with a column-count mismatch.
  This pattern (multiple sync locations for one logical change) is the
  prompt-versioning brainstorm's separate item (`database-migration-refactor`)
  that should consolidate these into a single declarative schema.

- **The `_migrate_generated_resumes_fk_cascade` recreate path is
  defensive code that's hard to test naturally.** It only fires on
  legacy pre-CASCADE DBs. The test #11c had to seed the legacy shape
  by hand (raw `executescript` with the historical CREATE TABLE SQL).
  This is brittle — if the historical shape ever changes via a force
  push or someone rewrites the legacy seed, the test passes against
  the wrong baseline. Worth a follow-up: pull the legacy DDL into a
  fixture file the test reads, and lock it under a git pre-commit hook.

- **Backwards-compat sweep was bigger than estimated.** The IMPL_PLAN
  estimated ~33 mechanical edits across 6 files; the actual was ~27
  (5 files, since `test_pdf_api.py` collapsed). Still big enough that
  hand-editing each one would have been error-prone; the conftest
  helper (`create_llm_result`) was the right abstraction even though
  it added one new shared dependency.

---

## What the next similar feature should do differently

- **Plan against assignment-count, not decorator-count.** When estimating
  test-mock sweeps, run `grep -c "mock_llm.return_value\s*=" file` not
  `grep -c "@patch.*mock_llm"`. Helper-based tests collapse on the
  decorator count.

- **Use a CST/AST transformer the first time.** For any mechanical sweep
  > 10 occurrences, write the transformer as a libcst (or `ast` + manual
  patching) pass rather than line-by-line regex. The 5-minute setup pays
  off in correctness.

- **Add the conftest helper BEFORE the sweep.** I added `create_llm_result`
  to `conftest.py` then ran the sweep. That's the right order — but
  this would be a documentable pattern for the v6-feature skill: "if a
  return-shape change touches > 5 tests, write a conftest wrapper
  helper first."

- **Run lean-code-reviewer mid-implementation, not just at the end.**
  By the time the review caught `t0`, that abbreviation had been pattern-copied
  to `gemini.py` and used as a model in the test descriptions. A
  mid-implementation review on `claude.py` would have stopped the spread.

- **For backend-only ceremony-M features, skip the inspector explicitly
  in the workflow.** The v6-feature spec only skips inspect for ceremony-XS
  + backend-only. For M, the inspector dispatches but has no UX_DESIGN
  to consume — it becomes a no-op. Spec the skip rule as "skip if
  UX_DESIGN is absent" rather than "skip if XS and backend."

---

## Carry-forward notes for the initiative

This slice unlocks three follow-on items (per the refined backlog):
- `prompts-as-files` — once those files exist, `prompt_path` becomes a
  meaningful file path. The current value `"services/llm/base.py:SYSTEM_PROMPT"`
  is a string sentinel. Item 2 should update both providers to read the
  file path of the actual loaded prompt.
- `framework-prod-importer` — the breadcrumbs schema this slice persists
  is what the importer reads. Schema:
  `(prompt_path, prompt_hash, provider, model, profile_snapshot,
   raw_output, latency_ms, input_tokens, output_tokens)` plus existing
  columns. Importer must handle NULL for legacy rows (`input_tokens`
  can be NULL on Gemini even on success).
- `retro-prompts-delegate-grading` — the existing `/retro-prompts` skill's
  "Reconstruct the trail" step now has every field it needs in one row.
  The hand-verification step (Scenario 6 of FEATURE_SPEC) was deferred
  to the skill-rewrite item, not done here.
