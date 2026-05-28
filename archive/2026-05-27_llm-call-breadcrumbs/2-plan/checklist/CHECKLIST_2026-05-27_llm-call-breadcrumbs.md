feature: llm-call-breadcrumbs
date: 2026-05-27
total_checkboxes: 74  (was 66 — added 8 after plan-reviewer ISSUES patch: 6 per-file sweep rows replacing 1 generic, +1 sweep-verify, +1 recreate-path test, +1 mid-call-exception test; net +8)
derived_from: IMPL_PLAN_2026-05-27_llm-call-breadcrumbs.md, FEATURE_SPEC_2026-05-27_llm-call-breadcrumbs.md, LIBRARY_NOTES_anthropic_2026-05-27.md, LIBRARY_NOTES_google-genai_2026-05-27.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: LIBRARY_NOTES_anthropic "runtime_constraint: Python >= 3.13" and LIBRARY_NOTES_google-genai "runtime_constraint: Python >= 3.13"
- [ ] Virtual environment created and activated  → source: IMPL_PLAN "All tests run via `uv run pytest -q`" (uv manages the venv)

---

## Section 1 — Dependencies

- [ ] `anthropic>=0.40.0` present in `pyproject.toml` (verify: `uv tree --package anthropic`)  → source: LIBRARY_NOTES_anthropic "version_constraint: >=0.40.0" and IMPL_PLAN "Library patterns" section
- [ ] `google-genai>=1.0.0` present in `pyproject.toml` (verify: `uv tree --package google-genai`)  → source: LIBRARY_NOTES_google-genai "version_constraint: >=1.0.0" and IMPL_PLAN "Library patterns" section

---

## Section 2 — Syntax

### 2.1 anthropic patterns

- [ ] `message.usage.input_tokens` read as bare `int` with NO None-guard at `services/llm/claude.py` breadcrumbs block  → source: LIBRARY_NOTES_anthropic "Patterns §2 — `input_tokens` and `output_tokens` are declared as bare `int`… never None on success"
- [ ] `message.usage.output_tokens` read as bare `int` with NO None-guard at `services/llm/claude.py` breadcrumbs block  → source: LIBRARY_NOTES_anthropic "Patterns §2 — bare `int`… required fields"
- [ ] `message.content[0].text` used as the canonical text-extraction pattern at `services/llm/claude.py` (not `message.content[0].value` or similar)  → source: LIBRARY_NOTES_anthropic "Patterns §4 — `message.content[0].text` confirmed canonical for non-streaming responses"

### 2.2 google-genai patterns

- [ ] `usage = getattr(response, "usage_metadata", None)` used as the outer None-guard at `services/llm/gemini.py` breadcrumbs block  → source: LIBRARY_NOTES_google-genai "Patterns §3 — `usage_metadata` can be `None`; use getattr guard"
- [ ] Each token sub-field guarded with `is not None` BEFORE use at `services/llm/gemini.py` (not just outer getattr)  → source: LIBRARY_NOTES_google-genai "Patterns §4 — every sub-field is individually optional / `None`… a `None` check is also needed"
- [ ] `usage.prompt_token_count` used for input tokens (not `input_token_count` or `prompt_tokens`) at `services/llm/gemini.py`  → source: LIBRARY_NOTES_google-genai "Patterns §2 — Python field name: `prompt_token_count`"
- [ ] `usage.candidates_token_count` used for output tokens at `services/llm/gemini.py`  → source: LIBRARY_NOTES_google-genai "Patterns §2 — Python field name: `candidates_token_count`"
- [ ] LIVE SPELLING VERIFICATION: run one real Gemini call (or a mock built from `vars(response.usage_metadata)`) and print the actual attribute names; confirm `candidates_token_count` is plural, not `candidate_token_count`  → source: LIBRARY_NOTES_google-genai "Open questions §2 — `candidates_token_count` vs `candidate_token_count`: verify once by printing `vars(response.usage_metadata)` in a live test call before shipping" and IMPL_PLAN §4 "Build-phase verification step"
- [ ] `response.text` used as the canonical text-extraction pattern at `services/llm/gemini.py`  → source: LIBRARY_NOTES_google-genai "Patterns §5 — `response.text` is the canonical one-liner for non-streaming text retrieval"

### 2.3 stdlib patterns

- [ ] `hashlib.sha1(prompt_text.encode("utf-8")).hexdigest()` used at `services/llm/claude.py` (SHA-1, not SHA-256; `encode("utf-8")` explicit)  → source: IMPL_PLAN "Library patterns — hashlib: `hashlib.sha1(prompt_text.encode("utf-8")).hexdigest()` produces a 40-char hex string"
- [ ] `hashlib.sha1(full_prompt.encode("utf-8")).hexdigest()` used at `services/llm/gemini.py` over the same concatenated `full_prompt` as passed to the SDK  → source: IMPL_PLAN "Library patterns — hashlib" and §4 "prompt_hash = hashlib.sha1(full_prompt.encode("utf-8")).hexdigest()"
- [ ] `t0 = time.monotonic()` and `latency_ms = int((time.monotonic() - t0) * 1000)` used at `services/llm/claude.py` (not `time.time()`)  → source: IMPL_PLAN "Library patterns — time: `time.monotonic()` returns a float; `int((t1 - t0) * 1000)` yields integer milliseconds" and FEATURE_SPEC "Non-functional notes — latency uses `time.monotonic()` so wall-clock jump doesn't produce garbage"
- [ ] Same `time.monotonic()` pattern used at `services/llm/gemini.py`  → source: IMPL_PLAN §4 and "Library patterns" section
- [ ] `json.dumps(profile, sort_keys=True, ensure_ascii=False)` used for `profile_snapshot` in both `services/llm/claude.py` and `services/llm/gemini.py`  → source: IMPL_PLAN "Library patterns — json: `json.dumps(profile, sort_keys=True, ensure_ascii=False)` produces deterministic, human-readable JSON"
- [ ] `import time` and `import hashlib` added at top of `services/llm/claude.py`  → source: IMPL_PLAN §3 "Imports to add at top of file: `import time`, `import hashlib`"
- [ ] `import time` and `import hashlib` added at top of `services/llm/gemini.py`  → source: IMPL_PLAN §4 "Same imports to add: `time`, `hashlib`"

---

## Section 3 — UX

n/a — no source (feature shape: backend-only, no UX_DESIGN provided)

---

## Section 4 — Tests

### 4.1 database.py migration (Scenario 1 / 1b)

- [ ] Unit test `test_fresh_install_includes_breadcrumb_columns` exists at `tests/test_database_migrations.py` — calls `init_db()` on a clean DB and asserts all 9 columns present via `PRAGMA table_info(generated_resumes)`  → source: IMPL_PLAN §11a and FEATURE_SPEC Scenario 1 "generated_resumes is created with all 9 breadcrumb columns inline"
- [ ] Unit test `test_init_db_idempotent_with_breadcrumb_columns` exists at `tests/test_database_migrations.py` — runs `init_db()` twice, asserts no exception and column set unchanged  → source: IMPL_PLAN §11b and FEATURE_SPEC Scenario 1 "calling init_db() a second time succeeds with zero ALTER TABLE errors"
- [ ] NEW test `test_recreate_path_preserves_breadcrumb_columns` exists at `tests/test_database_migrations.py` — seeds a legacy pre-CASCADE `generated_resumes` shape, calls `init_db()`, asserts the recreate path ran (CASCADE present in `sqlite_master.sql`) AND all 9 breadcrumb columns are present after recreate AND seeded rows survived with breadcrumb columns NULL  → source: IMPL_PLAN §11c "NEW, addresses ISSUE-3" — closes the untested-defensive-code gap on §1c/§1d

### 4.2 Claude provider (Scenario 2)

- [ ] Existing test `test_successful_generation` at `tests/test_claude_provider.py` destructures return as `result, _ = await ...`  → source: IMPL_PLAN §7a "Every existing test that calls `analyze_and_generate` must destructure… `result, _ = await claude_provider.analyze_and_generate(...)`"
- [ ] Existing test `test_extracts_json_from_mixed_response` at `tests/test_claude_provider.py` destructures return as `result, _`  → source: IMPL_PLAN §7a "Tests to touch: `test_extracts_json_from_mixed_response`"
- [ ] Existing test `test_language_parameter_passed` at `tests/test_claude_provider.py` destructures return as `result, _`  → source: IMPL_PLAN §7a "Tests to touch: `test_language_parameter_passed`"
- [ ] New test `test_breadcrumbs_populated_on_success` exists at `tests/test_claude_provider.py` and asserts: `provider == "claude"`, `prompt_path == "services/llm/base.py:SYSTEM_PROMPT"`, `prompt_hash` is 40-char `[0-9a-f]` hex, `input_tokens == 1234`, `output_tokens == 567`, `latency_ms >= 0`, `raw_output` equals mocked text, `profile_snapshot` round-trips via `json.loads`  → source: IMPL_PLAN §7b and FEATURE_SPEC Scenario 2 "prompt_hash = sha1 hex… 40 chars in [0-9a-f]… input_tokens = message.usage.input_tokens"

### 4.3 Gemini provider (Scenarios 3a, 3b)

- [ ] Existing test `test_successful_generation` at `tests/test_gemini_provider.py` destructures return as `result, _`  → source: IMPL_PLAN §8 "Same destructuring applied to: `test_successful_generation`"
- [ ] Existing test `test_extracts_json_from_response` at `tests/test_gemini_provider.py` destructures return as `result, _`  → source: IMPL_PLAN §8 "Tests to touch: `test_extracts_json_from_response`"
- [ ] Existing test `test_uses_custom_model_from_env` at `tests/test_gemini_provider.py` destructures return as `result, _`  → source: IMPL_PLAN §8 "Tests to touch: `test_uses_custom_model_from_env`"
- [ ] New test `test_breadcrumbs_populated_with_usage_metadata` exists at `tests/test_gemini_provider.py` — mocks `usage_metadata.prompt_token_count = 100`, `usage_metadata.candidates_token_count = 50`; asserts `input_tokens == 100`, `output_tokens == 50`, `provider == "gemini"`, `prompt_hash` is 40-char hex, `latency_ms >= 0`, `profile_snapshot` round-trips  → source: IMPL_PLAN §8a and FEATURE_SPEC Scenario 3a "input_tokens and output_tokens reflect the SDK values"
- [ ] New test `test_breadcrumbs_tokens_null_when_usage_metadata_missing` exists at `tests/test_gemini_provider.py` — mocks response with no `usage_metadata` attribute; asserts `input_tokens is None`, `output_tokens is None`, all other breadcrumbs populated  → source: IMPL_PLAN §8b and FEATURE_SPEC Scenario 3b "input_tokens IS NULL… output_tokens IS NULL… every other breadcrumb still populated"
- [ ] New test `test_breadcrumbs_tokens_null_when_subfield_is_none` exists at `tests/test_gemini_provider.py` — `usage_metadata` present but `prompt_token_count` is None; asserts NULL fall-through  → source: IMPL_PLAN §8c (optional but explicitly listed) and LIBRARY_NOTES_google-genai "Patterns §4 — sub-field can be `None`… `None` check also needed"

### 4.4 Resume persistence sweep (Scenario 2 photo assertion, Scenario 4)

- [ ] SWEEP (1/6) — `tests/test_resumes.py` (15 occurrences): every `@patch("services.resume_generator.llm_service.analyze_and_generate")` decorator's `mock_llm.return_value` is now a `(dict, dict)` tuple, not a bare dict  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP (2/6) — `tests/test_pdf_api.py` (8 occurrences): same tuple-shape conversion  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP (3/6) — `tests/test_resume_generator.py` (6 occurrences): same tuple-shape conversion  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP (4/6) — `tests/test_chronological_order.py` (3 occurrences): same tuple-shape conversion  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP (5/6) — `tests/test_jobs.py` (1 occurrence): same tuple-shape conversion  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP (6/6) — `tests/test_llm_service.py` (10 occurrences): not return-value mocks but `result = await llm_service.analyze_and_generate(...)` assignments need to destructure as `result, _ = await ...` (or accept that result is a tuple in assertions)  → source: IMPL_PLAN §9 sweep table
- [ ] SWEEP-VERIFY: `grep -rn "mock_llm.return_value = {" tests/` returns ZERO matches after the sweep (every mock now returns a tuple)  → source: IMPL_PLAN §9 "the sweep must be exhaustive"
- [ ] `test_generate_resume_success` at `tests/test_resumes.py` uses tuple-shaped `mock_llm.return_value = (parsed_dict, breadcrumbs_dict)`  → source: IMPL_PLAN §9 "The current mock returns a single dict. Change it to a `(dict, dict)` tuple"
- [ ] `test_get_resume_after_generation` at `tests/test_resumes.py` uses tuple-shaped mock return value  → source: IMPL_PLAN §9 "Tests to touch: `test_get_resume_after_generation`"
- [ ] `test_generate_resume_success` at `tests/test_resumes.py` includes post-INSERT assertions: `row["provider"] == "claude"`, `row["model"] == "claude-test-model"`, `row["prompt_hash"] == "a" * 40`, `row["raw_output"] is not None`, `row["profile_snapshot"] is not None`, `row["latency_ms"] == 42`, `row["input_tokens"] == 1000`, `row["output_tokens"] == 500`  → source: IMPL_PLAN §9 "after the existing success assertions, add…" and FEATURE_SPEC Scenario 2 success criteria
- [ ] `test_generate_resume_success` at `tests/test_resumes.py` asserts `"photo" not in json.loads(row["profile_snapshot"]).get("personal_info", {})`  → source: IMPL_PLAN §9 and FEATURE_SPEC §7 "Add an explicit assertion that `"photo" not in json.loads(row["profile_snapshot"]).get("personal_info", {})`"

### 4.5 Determinism and snapshot-timing tests (Scenario 4, Scenario 2 photo)

- [ ] New test `test_prompt_hash_deterministic_across_runs` exists at `tests/test_resume_generator.py` — calls `generate(...)` twice with same inputs, queries both rows, asserts `row1["prompt_hash"] == row2["prompt_hash"]` and `row1["profile_snapshot"] == row2["profile_snapshot"]`  → source: IMPL_PLAN §10a and FEATURE_SPEC Scenario 4 "row1.prompt_hash == row2.prompt_hash byte-for-byte… row1.profile_snapshot == row2.profile_snapshot byte-for-byte"
- [ ] New test `test_profile_snapshot_omits_photo` exists at `tests/test_resume_generator.py` — profile has `personal_info.photo`; mock provider captures what it receives; asserts `"photo" not in json.loads(row["profile_snapshot"]).get("personal_info", {})`  → source: IMPL_PLAN §10b "closes the snapshot-timing concern from analysis-reviewer Issue #2" and FEATURE_SPEC success criteria "json.loads(row["profile_snapshot"]).get("personal_info", {}) does NOT contain a `"photo"` key"

### 4.6 Error path (Scenario 5) — NEW TEST (resolves plan-reviewer ISSUE-2)

- [ ] New test `test_no_row_inserted_on_llm_exception` exists at `tests/test_resume_generator.py` — calls `resume_generator_service.generate(...)` with `analyze_and_generate` mocked to raise `ConnectionError`, asserts `pytest.raises(ConnectionError)` AND asserts the `generated_resumes` row count is unchanged before vs after the call  → source: IMPL_PLAN §10c "NEW TEST, addresses ISSUE-2" and FEATURE_SPEC Scenario 5 "no row is INSERTed into generated_resumes"
- [ ] Error-path tests in `tests/test_claude_provider.py` and `tests/test_gemini_provider.py` (the existing tests that assert on `pytest.raises(...)`) still pass without modification — they don't reach the return value, so destructuring is irrelevant  → source: IMPL_PLAN §7a "Error-path tests don't reach the return — they assert on raise. No change."

---

## Section 5 — Accessibility

n/a — no source (no UX_DESIGN; feature shape is backend-only)

---

## Section 6 — Implementation correctness (per-location sync)

These checkboxes are derived from the IMPL_PLAN's explicit four-location sync requirement for `database.py` and from the annotation-without-gate requirement for `services/llm/__init__.py`. They have no automated gate and must be verified by hand.

### 6.1 database.py — four locations (must stay in sync)

- [ ] **Location 1a** — Inline DDL at `database.py:339-353` (`CREATE TABLE IF NOT EXISTS generated_resumes`): all 9 breadcrumb columns (`prompt_path TEXT`, `prompt_hash TEXT`, `provider TEXT`, `model TEXT`, `profile_snapshot TEXT`, `raw_output TEXT`, `latency_ms INTEGER`, `input_tokens INTEGER`, `output_tokens INTEGER`) appear BEFORE the `FOREIGN KEY` clause  → source: IMPL_PLAN §1a and FEATURE_SPEC §1 "Inline DDL at `database.py:339-353`… gains the 9 new columns"
- [ ] **Location 1b** — Migrations list at `database.py:357-376`: 9 new `ALTER TABLE generated_resumes ADD COLUMN <name> <type>` entries appended AT THE END of the `migrations = [...]` list, one per column, in the same order as 1a  → source: IMPL_PLAN §1b "Appended AT THE END so any production DB… doesn't get insertion-order shift"
- [ ] **Location 1c** — `_migrate_generated_resumes_fk_cascade` CREATE block at `database.py:207-222` (`CREATE TABLE generated_resumes_new`): same 9 column declarations added in the same position as 1a (before FK clause)  → source: IMPL_PLAN §1c "add the 9 column declarations to the `CREATE TABLE generated_resumes_new (...)` SQL"
- [ ] **Location 1d** — `_migrate_generated_resumes_fk_cascade` INSERT/SELECT at `database.py:228-234`: all 9 column names appear in BOTH the INSERT target list AND the SELECT source list, in matching order  → source: IMPL_PLAN §1d "add the 9 column names to both the INSERT target list and the SELECT source list, in matching order"
- [ ] All four locations list the 9 columns in identical order: `prompt_path`, `prompt_hash`, `provider`, `model`, `profile_snapshot`, `raw_output`, `latency_ms`, `input_tokens`, `output_tokens`  → source: IMPL_PLAN §1 "Column order in INSERT matches the appended order in the inline DDL (#1a) and the migrations list (#1b)" and risks table "all four locations must stay in sync"

### 6.2 services/llm/base.py — Protocol annotation

- [ ] `analyze_and_generate` return-type annotation in `services/llm/base.py` changed from `-> dict` to `-> tuple[dict, dict]`  → source: IMPL_PLAN §2a "Update `analyze_and_generate` return-type annotation from `dict` to `tuple[dict, dict]`"
- [ ] Docstring Returns section in `services/llm/base.py` describes both tuple elements: parsed JSON dict and breadcrumbs dict with the 9 provider-owned fields  → source: IMPL_PLAN §2a "update the docstring's Returns section to describe both elements"

### 6.3 services/llm/__init__.py — annotation with no automated gate

- [ ] `_LazyLLMService.analyze_and_generate` return annotation at `services/llm/__init__.py` is literally `-> tuple[dict, dict]` (not `-> dict`, not `-> Tuple`, not missing)  → source: IMPL_PLAN §5a "Change return annotation `-> dict` to `-> tuple[dict, dict]`" and FEATURE_SPEC §6 "CHECKLIST note: this annotation change has no runtime test gate today… must list this as its own explicit line item so it doesn't get skipped"
- [ ] Docstring Returns section in `services/llm/__init__.py` updated to describe the tuple  → source: IMPL_PLAN §5b "Change the docstring's Returns section to describe the tuple"
- [ ] Function body of `_LazyLLMService.analyze_and_generate` is UNCHANGED — still `await self._get_instance().analyze_and_generate(...)` with no manual tuple construction  → source: IMPL_PLAN §5c "The function body already forwards via `await self._get_instance().analyze_and_generate(...)` — no body change needed"

### 6.4 services/llm/claude.py — breadcrumbs implementation

- [ ] `profile_snapshot` is materialized BEFORE the `client.messages.create(...)` call (capture the photo-stripped state, not the post-call state)  → source: IMPL_PLAN §3 "profile_snapshot is materialized at the top of the function, BEFORE the SDK call"
- [ ] `prompt_text` concatenation uses `SYSTEM_PROMPT + "\n\n" + user_prompt` (double newline separator, matching Gemini's concatenation)  → source: IMPL_PLAN §3 "This exact concatenation lets the hash match what Gemini's hash would be for the same inputs"
- [ ] `latency_ms` timer wraps the `client.messages.create(...)` call ONLY — does not include JSON parsing  → source: IMPL_PLAN §3 "`latency_ms` is measured around the SDK call ONLY, not around JSON parsing"
- [ ] Return statement is `return result, breadcrumbs` (tuple, not a single dict)  → source: IMPL_PLAN §3 final line

### 6.5 services/llm/gemini.py — breadcrumbs implementation

- [ ] `profile_snapshot` is materialized BEFORE the `client.aio.models.generate_content(...)` call  → source: IMPL_PLAN §4 "existing prelude — then `profile_snapshot = ...`" (listed before the SDK call block)
- [ ] `prompt_hash` is over `full_prompt` (the actual concatenated string passed to the SDK), not over `SYSTEM_PROMPT` alone  → source: IMPL_PLAN §4 "`prompt_hash = hashlib.sha1(full_prompt.encode("utf-8")).hexdigest()`"
- [ ] `latency_ms` timer wraps the `client.aio.models.generate_content(...)` call ONLY  → source: IMPL_PLAN §4 same latency-scope rule as Claude
- [ ] Return statement is `return result, breadcrumbs`  → source: IMPL_PLAN §4 final line

### 6.6 services/resume_generator.py — destructure and persist

- [ ] Line 49 of `services/resume_generator.py` changed to `llm_result, breadcrumbs = await llm_service.analyze_and_generate(...)`  → source: IMPL_PLAN §6a "Change line 49 from `llm_result = await...` to `llm_result, breadcrumbs = await...`"
- [ ] INSERT at `services/resume_generator.py:88-103` includes all 9 new columns in the SQL column list: `prompt_path`, `prompt_hash`, `provider`, `model`, `profile_snapshot`, `raw_output`, `latency_ms`, `input_tokens`, `output_tokens`  → source: IMPL_PLAN §6b full INSERT block
- [ ] INSERT parameter tuple binds breadcrumbs using direct dict indexing (`breadcrumbs["prompt_path"]` etc.), NOT `.get(..., None)`  → source: IMPL_PLAN §6b "The parameter binding uses direct dict indexing (not `.get(..., None)`) — every key in `breadcrumbs` is guaranteed populated by the provider"
- [ ] Total placeholder count in the VALUES clause is 16 (7 existing + 9 new) and matches the parameter tuple length  → source: IMPL_PLAN §6b VALUES clause `(?, ?, ?, ?, ?, ?, ?,  ?, ?, ?, ?, ?, ?, ?, ?, ?)`
- [ ] `schemas.py` is NOT modified (API response model deliberately omits breadcrumbs)  → source: FEATURE_SPEC §9 "`schemas.py` is not modified… omits breadcrumbs — they are internal-only"

### 6.7 tests/test_database_migrations.py — new file header

- [ ] New file `tests/test_database_migrations.py` has a module-level docstring matching the scope-statement style of sibling test files  → source: IMPL_PLAN "Lean-code rule compliance — New test file `tests/test_database_migrations.py` gets a docstring header matching the style of sibling test files"

---

## Section 7 — Run gate

- [ ] `uv run pytest -q` passes with zero failures after all changes  → source: IMPL_PLAN "Test plan summary — All tests run via `uv run pytest -q`" and "Pre-existing test count must remain identical (no test deletion)"
- [ ] Pre-existing test count is unchanged (no test was deleted as a side-effect of this slice)  → source: IMPL_PLAN "Pre-existing test count must remain identical (no test deletion)"
