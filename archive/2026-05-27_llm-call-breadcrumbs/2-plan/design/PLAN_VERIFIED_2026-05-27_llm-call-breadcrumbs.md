feature: llm-call-breadcrumbs
date: 2026-05-27
status: ISSUES
reviewer: plan-reviewer
inputs_reviewed:
  - workbench/1-analyze/spec/FEATURE_SPEC_2026-05-27_llm-call-breadcrumbs.md
  - workbench/2-plan/design/IMPL_PLAN_2026-05-27_llm-call-breadcrumbs.md
  - workbench/2-plan/checklist/CHECKLIST_2026-05-27_llm-call-breadcrumbs.md
  - workbench/2-plan/research/LIBRARY_NOTES_anthropic_2026-05-27.md
  - workbench/2-plan/research/LIBRARY_NOTES_google-genai_2026-05-27.md

---

## 1. Traceability table (FEATURE_SPEC Must-Have → IMPL_PLAN)

| # | Requirement (FEATURE_SPEC) | Covered by IMPL_PLAN | Status |
|---|---|---|---|
| 1.1 | Inline DDL at `database.py:339-353` gains 9 columns | §1a | covered |
| 1.2 | Append 9 ALTER TABLE entries to migrations at `database.py:357-376` | §1b | covered |
| 1.3 | `_migrate_generated_resumes_fk_cascade` CREATE block (`database.py:207-222`) gets 9 columns | §1c | covered |
| 1.4 | `_migrate_generated_resumes_fk_cascade` INSERT/SELECT (`database.py:228-234`) gets 9 columns | §1d | covered |
| 2   | `LLMProvider` protocol returns `tuple[dict, dict]` from `analyze_and_generate` | §2a | covered |
| 3   | `ClaudeProvider.analyze_and_generate` returns breadcrumbs with 9 fields | §3 | covered |
| 4   | `GeminiProvider.analyze_and_generate` returns breadcrumbs with usage_metadata two-level guard | §4 | covered |
| 5   | `ResumeGeneratorService.generate` destructures tuple and persists 9 columns; preserves call ordering | §6a, §6b, §6c | covered |
| 6   | `_LazyLLMService.analyze_and_generate` annotation updated to `-> tuple[dict, dict]`, forwards unchanged | §5 | covered |
| 7a  | `tests/test_claude_provider.py` — 1 new test + destructure existing | §7a, §7b | covered |
| 7b  | `tests/test_gemini_provider.py` — 2 populated/missing tests + destructure | §8a, §8b, §8c | covered |
| 7c  | `tests/test_resumes.py` — extend test_generate_resume_success + photo assertion | §9 | covered |
| 7d  | `tests/test_resume_generator.py` — determinism end-to-end test | §10a, §10b | covered |
| 8   | Migration entries appended at end of list | §1b | covered |
| 9   | `schemas.py` NOT modified | (negative; CHECKLIST §6.6 row 5) | covered |

All 9 must-haves are addressed in the plan.

---

## 2. File-path verification (anti-hallucination)

| Reference | Type | Exists | Status |
|---|---|---|---|
| `database.py` | modify | yes | OK |
| `database.py:339-353` (inline DDL CREATE TABLE generated_resumes) | modify | yes — `CREATE TABLE` line 339, body 340-348, FK 348, closing 349; trailing index 351-353. Plan's "339-353" overstates the block end by including the trailing INDEX statement but the FK-clause anchor at line 348 is correct. | OK (minor) |
| `database.py:357-376` (migrations list) | modify | yes — exact match | OK |
| `database.py:207-222` (CREATE TABLE generated_resumes_new) | modify | yes — exact match (CREATE TABLE on 207, closing `""")` on 222) | OK |
| `database.py:228-234` (INSERT/SELECT lists) | modify | yes — INSERT block at 228; SELECT at 232; FROM at 235; closing `""")` at 236. The cited range "228-234" stops at the SELECT body's penultimate line; the actual `FROM generated_resumes` is at line 235 and the closing triple-quote at line 236. | OK (minor — off by 1-2 lines) |
| `database.py:441` (call to `_migrate_generated_resumes_fk_cascade`) | reference | yes — exact match | OK |
| `_migrate_generated_resumes_fk_cascade` early-return at "line 199" | reference (in spec) | line 199 is the `if` condition; line 200 is the actual `return` | MINOR (off-by-one in FEATURE_SPEC §1.3 wording, also in CHECKLIST/IMPL_PLAN footnotes; harmless) |
| `services/llm/base.py` (SYSTEM_PROMPT defined at line 40) | modify | yes | OK |
| `services/llm/claude.py` (`ClaudeProvider.analyze_and_generate` at line 40) | modify | yes | OK |
| `services/llm/gemini.py` | modify | yes | OK |
| `services/llm/gemini.py:76` (`full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"`) | reference | yes — exact match line 76 | OK |
| `services/llm/__init__.py` (`_LazyLLMService.analyze_and_generate` at line 32) | modify | yes | OK |
| `services/resume_generator.py` | modify | yes | OK |
| `services/resume_generator.py:34-53` (photo-strip window) | reference | yes — covers `profile_dict = profile.model_dump()` to photo restore | OK |
| `services/resume_generator.py:41` (`del profile_dict["personal_info"]["photo"]`) | reference | yes — exact match | OK |
| `services/resume_generator.py:49` (`llm_result = await llm_service.analyze_and_generate(...)`) | modify | yes — exact match | OK |
| `services/resume_generator.py:61` (`saved_job_id = job_service.save_job_analysis(`) | reference | yes — exact match | OK |
| `services/resume_generator.py:88-103` (INSERT INTO generated_resumes) | modify | yes — `cursor = conn.execute(` line 88, closing `)` line 103 | OK |
| `tests/test_claude_provider.py` | modify | yes | OK |
| `tests/test_gemini_provider.py` | modify | yes | OK |
| `tests/test_resumes.py` | modify | yes | OK |
| `tests/test_resume_generator.py` | modify | yes | OK |
| `tests/test_database_migrations.py` | create | parent dir `tests/` exists, file does not (correct — plan creates) | OK |
| Symbol: `ClaudeProvider.analyze_and_generate` | modify | yes — line 40 of claude.py | OK |
| Symbol: `GeminiProvider.analyze_and_generate` | modify | yes — line 40 of gemini.py | OK |
| Symbol: `_LazyLLMService.analyze_and_generate` | modify | yes — line 32 of `__init__.py` | OK |
| Symbol: `_get_model()` (claude & gemini) | reference | yes (both at line 32) | OK |
| Symbol: `_migrate_generated_resumes_fk_cascade` | modify | yes (line 182 of database.py) | OK |
| Existing test `test_successful_generation` in test_claude_provider.py | modify | yes (line 43) | OK |
| Existing test `test_extracts_json_from_mixed_response` | modify | yes (line 80) | OK |
| Existing test `test_language_parameter_passed` | modify | yes (line 100) | OK |
| Existing test `test_successful_generation` in test_gemini_provider.py | modify | yes (line 43) | OK |
| Existing test `test_extracts_json_from_response` | modify | yes (line 69) | OK |
| Existing test `test_uses_custom_model_from_env` | modify | yes (line 90) | OK |
| Existing test `test_generate_resume_success` in test_resumes.py | modify | yes (line 52, with decorator on 51) | OK |
| Existing test `test_get_resume_after_generation` | modify | yes (line 97) | OK |

No hallucinated file paths. No hallucinated function/method symbols. Line ranges have minor (1-2 line) off-by-one errors that the implementer can self-correct, no semantic risk.

---

## 3. Library-pattern verification

| Pattern (IMPL_PLAN) | Documented in | Status |
|---|---|---|
| `message.usage.input_tokens` is bare `int`, never None | LIBRARY_NOTES_anthropic §2 (verbatim: "bare `int`… never None on success") | OK (verbatim match) |
| `message.usage.output_tokens` is bare `int`, never None | LIBRARY_NOTES_anthropic §2 | OK |
| `message.content[0].text` for non-streaming | LIBRARY_NOTES_anthropic §4 | OK |
| Gemini: `getattr(response, "usage_metadata", None)` two-level guard | LIBRARY_NOTES_google-genai §4 ("the spec's defensive `try/except AttributeError` pattern is correct AND insufficient on its own — a `None` check is also needed") | OK (this matches verbatim; the IMPL_PLAN's two-layer guard pattern is the stronger pattern the LIBRARY_NOTES explicitly recommended) |
| Gemini: `usage.prompt_token_count` field name | LIBRARY_NOTES_google-genai §2 | OK |
| Gemini: `usage.candidates_token_count` field name | LIBRARY_NOTES_google-genai §2 (plus Open question §2 about plural vs singular) | OK (plan acknowledges residual uncertainty; defensive guard ensures graceful degradation) |
| `response.text` for Gemini non-streaming | LIBRARY_NOTES_google-genai §5 | OK |
| `hashlib.sha1(...).hexdigest()` — stdlib | Python 3.13 stdlib, confirmed via local Python run (`a94a8fe5ccb19ba61c4c0873d391e987982fbbd3` for `b'test'` — works) | OK |
| `time.monotonic()` → float | Python 3.13 stdlib, confirmed | OK |
| `json.dumps(..., sort_keys=True, ensure_ascii=False)` | Python 3.13 stdlib, confirmed | OK |

There is, however, a **divergence note** worth flagging: FEATURE_SPEC §3 still mentions `getattr(message.usage, "input_tokens", None)` for Claude. IMPL_PLAN §3 deliberately drops the `getattr` and reads `message.usage.input_tokens` directly, citing LIBRARY_NOTES_anthropic. This is a deliberate, documented downgrade of the spec's over-defensive pattern; the LIBRARY_NOTES explicitly states "the `getattr(...)` pattern in the FEATURE_SPEC is therefore safe but over-defensive". The CHECKLIST §2.1 reinforces "NO None-guard". Plan is internally consistent and the spec language is the over-defensive variant. MINOR observation only.

---

## 4. Checklist coverage (IMPL_PLAN file → CHECKLIST items)

| Plan file/section | Checklist items | Status |
|---|---|---|
| §1a (DDL line 339-353) | §6.1 Location 1a + §6.1 final ordering row | covered |
| §1b (migrations list 357-376) | §6.1 Location 1b | covered |
| §1c (recreate CREATE 207-222) | §6.1 Location 1c | covered |
| §1d (recreate INSERT/SELECT 228-234) | §6.1 Location 1d | covered |
| §2a (base.py annotation + docstring) | §6.2 (both rows) | covered |
| §3 (claude.py breadcrumbs) | §2.1 (3 rows) + §2.3 (4 stdlib rows) + §6.4 (4 rows) | covered |
| §4 (gemini.py breadcrumbs) | §2.2 (5 rows including live verification) + §6.5 (4 rows) | covered |
| §5 (`__init__.py` wrapper) | §6.3 (3 rows including unchanged-body assertion) | covered |
| §6a/6b/6c (resume_generator) | §6.6 (5 rows) | covered |
| §7a (claude existing tests destructure) | §4.2 (3 destructure rows) | covered |
| §7b (claude new test) | §4.2 (`test_breadcrumbs_populated_on_success`) | covered |
| §8a/8b/8c (gemini new tests) | §4.3 (3 new-test rows) | covered |
| §8 (gemini existing tests destructure) | §4.3 (3 destructure rows) | covered |
| §9 (test_resumes.py) | §4.4 (5 rows: sweep + 2 tuple mocks + persistence + photo) | covered |
| §10a (determinism) | §4.5 row 1 | covered |
| §10b (snapshot-no-photo) | §4.5 row 2 | covered |
| §11a/11b (test_database_migrations.py) | §4.1 (2 rows) + §6.7 (docstring) | covered |
| Implementation order (§Implementation order) | §7 (run gate) | covered |
| Scenario 5 (existing LLM-error test still passes) | §4.6 | covered — BUT see finding ISSUE-2 below |

No orphan checklist items observed. No IMPL_PLAN file/section without checklist coverage. **However, the checklist inherits one specific defect from the spec (see Risks §5 below).**

---

## 5. Risks and ambiguities (findings)

### ISSUE-1 — [MAJOR] Test-sweep scope dramatically underestimated

**Location:** `IMPL_PLAN §9` ("Tests to touch: `test_generate_resume_success`, `test_get_resume_after_generation`, Any other test in the file that mocks `llm_service.analyze_and_generate` — sweep with a search.") and the IMPL_PLAN risks-table row "Forgetting to destructure in existing tests | MEDIUM | >=2 occurrences in `test_resumes.py`".

**Concrete failure mode:** the plan estimates ">=2 occurrences in `test_resumes.py`". The actual count is **15 occurrences in `test_resumes.py`** plus **6 in `test_resume_generator.py`**, **3 in `test_chronological_order.py`**, **8 in `test_pdf_api.py`**, **1 in `test_jobs.py`**. Total: **33 distinct `@patch("services.resume_generator.llm_service.analyze_and_generate")` decorators across 5 test files**, all of which set `mock_llm.return_value = { ... }` to a single dict — every one of them will fail with "cannot unpack non-iterable dict object" at line 49 of `resume_generator.py` after the destructure lands.

The CHECKLIST §4.4 has one row that says "SWEEP: every test in `tests/` that mocks `analyze_and_generate`…" which technically covers this. But the IMPL_PLAN's risks-table likelihood ("MEDIUM, >=2 occurrences in `test_resumes.py`") is wildly off — it's HIGH-certainty, ~33 occurrences across the whole `tests/` tree. The "Modified tests: ~6" line in the IMPL_PLAN's "Test plan summary" is similarly off by ~5x. The IMPL_PLAN does not enumerate the affected files outside `test_resumes.py`/`test_resume_generator.py`/the provider tests, so an implementer following the plan literally will miss `test_pdf_api.py`, `test_chronological_order.py`, and `test_jobs.py` entirely.

**Why MAJOR not MINOR:** missing even one test file = the whole `uv run pytest -q` gate fails. The plan's Run gate (CHECKLIST §7) cannot pass unless the sweep is exhaustive. A "MEDIUM" risk that's actually a near-certain failure under-prepares the implementer.

**Diagnosis only:** Plan needs to either (a) explicitly enumerate the 5 affected test files and the per-file count, or (b) elevate the risk to HIGH and require the implementer to grep the full `tests/` tree before declaring done. The CHECKLIST already has the sweep gate; the IMPL_PLAN's prose just doesn't match the magnitude.

### ISSUE-2 — [MAJOR] Scenario 5 references a test that does NOT exist

**Location:** `FEATURE_SPEC §7` and `IMPL_PLAN §3` final paragraph ("The exception propagates and no row is INSERTed (caller doesn't reach the INSERT — see #5). This matches Scenario 5 of the spec.") and `FEATURE_SPEC BDD Scenario 5` ("the existing test in tests/test_resumes.py that asserts 'no row created on LLM error' continues to pass without modification.") and `CHECKLIST §4.6` ("Existing 'no row created on LLM error' test at `tests/test_resumes.py` still passes without modification").

**Concrete failure mode:** No such test exists. Grepping `test_resumes.py` and `test_resume_generator.py` for `side_effect`, `APIConnectionError`, `APIError`, `ConnectionError`, `RaiseError`, `def test_*error*`, `def test_*exception*`, `def test_*fail*` returns ZERO matches. The provider-level error-path tests (e.g., `test_connection_error_mapped` in `test_claude_provider.py:126`) exercise the provider's exception mapping but do NOT exercise the caller path through `ResumeGeneratorService.generate` to assert no `generated_resumes` row was INSERTed.

Consequence: CHECKLIST §4.6 cannot be verified — the gate references a test that does not exist. Worse, Scenario 5 ("Mid-call exception writes no breadcrumb row") is a success criterion in the spec but has no executable evidence. If the implementer notices, they have to invent a new test (out of scope per IMPL_PLAN §10's count of "5 new tests"); if they don't notice, the spec's coverage is fictional.

**Diagnosis only:** The plan and spec both make a load-bearing claim about an existing test that the codebase does not contain. Resolution path is for the parent to either (a) accept Scenario 5 as untested and remove the gate, (b) add a new test for it (raising the new-test count from 5 to 6), or (c) explicitly justify why no test is needed (the call-order analysis alone is sufficient).

### ISSUE-3 — [MAJOR] Pre-CASCADE legacy path (Scenario 1b's sibling Scenario 1c) has no executable test in this slice

**Location:** `IMPL_PLAN §11` (last paragraph: "The post-CASCADE upgrade-path test and the pre-CASCADE legacy-path test are deliberately out of scope here — they belong to `database-migration-refactor`. This slice only tests its own additions.") and `FEATURE_SPEC` "Success criteria — Migration-state-specific criteria — Pre-CASCADE legacy path".

**Concrete failure mode:** the spec promises three migration paths converge on the same final shape. The plan only writes a test for the fresh-install path (§11a) and an idempotency test (§11b). The Post-CASCADE upgrade path AND the Pre-CASCADE legacy path are deferred to a separate backlog item. The IMPL_PLAN explicitly defends this with "this slice only tests its own additions" — but §1c and §1d ARE additions to this slice, specifically targeting the recreate path. Adding code to `_migrate_generated_resumes_fk_cascade` without a test that exercises the recreate path leaves the BLOCKER-level risk identified by analysis-reviewer (recreate path silently drops new columns if the inline DDL diverges from the recreate CREATE block) **partially unverified**.

The risks table in IMPL_PLAN row 5 acknowledges this: "SQLite migration's recreate path fires on a real fresh install | LOW (current production state is post-CASCADE) | Test #11a covers fresh install; recreate block has been patched (#1c, #1d) to include breadcrumb columns even when it fires" — but a fresh-install test does NOT exercise the recreate path on a pre-CASCADE DB. The mitigation cited (`test #11a`) covers a different code path.

**Why MAJOR not BLOCKER:** the spec explicitly lists "Pre-CASCADE legacy path" as a hypothetical state ("most likely a historical clone"), and IMPL_PLAN argues this is improbable. If the implementer trusts the LOW likelihood, the slice ships; if a pre-CASCADE DB exists in the wild and is hit, the legacy data loses breadcrumb columns from the recreate. Worst case is data inconsistency in a corner-case DB, not crash. Not BLOCKER because production is post-CASCADE; MAJOR because the plan added code to §1c/§1d specifically to defend against this scenario and then declared it out of scope to test.

**Diagnosis only:** the plan either needs a smoke test that recreates the recreate-path conditions and asserts breadcrumb columns survive, OR it needs to admit Section 1c/1d is untested defensive code with no executable proof.

### ISSUE-4 — [MINOR] IMPL_PLAN §3 "test_breadcrumbs_populated_on_success" assertions split mid-bullet, contradicts itself on photo-stripping responsibility

**Location:** `IMPL_PLAN §7b`, the bullet about `profile_snapshot`:

> "Add a sub-test where the profile has a photo and the snapshot HAS the photo too — correct provider behavior — to clarify the contract"

But this contradicts FEATURE_SPEC §7 (and the entire snapshot-timing argument):
> "Add an explicit assertion that `"photo" not in json.loads(row["profile_snapshot"]).get("personal_info", {})`"

The plan is internally inconsistent: it says (a) at the provider unit test level, if a photo is in the input dict the provider SHOULD snapshot it (because the provider's contract is "snapshot what I received"), AND (b) the integration test at §10b asserts no photo in the snapshot. Both are correct in isolation — provider unit test ≠ integration test — but the IMPL_PLAN §7b bullet is ambiguously phrased and risks a confused implementer writing the wrong assertion.

**Diagnosis only:** rephrase §7b to clarify the provider unit test treats the photo as "what the provider received" and the integration test asserts the caller stripped it correctly. CHECKLIST §4.5 already gets this right; the bug is only in the IMPL_PLAN prose.

### ISSUE-5 — [MINOR] Line range "208" and "228-234" cited but actual closing is 222 and 236

**Location:** `IMPL_PLAN §1c` ("CREATE block at `database.py:207-222`") and `§1d` ("INSERT/SELECT lists at `database.py:228-234`").

**Concrete failure mode:** the cited ranges are accurate at the start (207, 228) and approximately correct at the end (CREATE TABLE block ends at line 222, the closing `""")` — exact match; INSERT/SELECT block ends at line 236 with the closing `""")`, but plan cites 234). A diff tool will catch the right context, but if a future maintainer searches for line "234" expecting INSERT/SELECT they will land in the middle of the SELECT body. Trivial impact.

**Diagnosis only:** rephrase to "lines 227-236" or "the INSERT/SELECT block beginning at line 228".

### ISSUE-6 — [MINOR] Plan says "the spec's `try/except AttributeError` would catch the first layer only" but the spec actually says "wrap the read in `try/except AttributeError` and NULL both counts on any access failure"

**Location:** `IMPL_PLAN §4` ("The spec's `try/except AttributeError` would catch the first layer only; this pattern catches both.")

**Concrete failure mode:** misreading. `FEATURE_SPEC §4` says to wrap the read in `try/except AttributeError`. A try/except around `usage.prompt_token_count` access DOES catch both layers if `usage_metadata` is None (the access raises `AttributeError` on `None.prompt_token_count`). The plan's `getattr` + `is not None` pattern is more robust against sub-field `None` values (which would NOT raise AttributeError but would be unusable as ints), but the plan's claim that try/except is insufficient is misleading. The actual defect of try/except is sub-field None-values (not AttributeError), and LIBRARY_NOTES_google-genai §4 confirms that.

**Diagnosis only:** rephrase to "spec's try/except handles attribute absence; this pattern additionally handles sub-field None values per LIBRARY_NOTES_google-genai §4."

### ISSUE-7 — [MINOR] `import json` already exists in claude.py and gemini.py — IMPL_PLAN's "Imports to add" doesn't say "json" but it's needed for the new `json.dumps(profile, sort_keys=True, ensure_ascii=False)`

**Location:** `IMPL_PLAN §3` "Imports to add at top of file: `import time`, `import hashlib`" and `§4` "Same imports to add: `time`, `hashlib`."

**Concrete failure mode:** both files already `import json` at line 4 — no change needed. The plan is correct (it lists only the new imports), but the omission of `json` is silent. Not a bug; just a verification that the implementer doesn't need to add json.

**Diagnosis only:** no fix required; flagged for explicit acknowledgment.

---

## 6. Summary count

- BLOCKER: 0
- MAJOR: 3 (ISSUE-1, ISSUE-2, ISSUE-3)
- MINOR: 4 (ISSUE-4, ISSUE-5, ISSUE-6, ISSUE-7)
- Hallucinated file paths: 0
- Hallucinated symbols: 0
- Checklist orphans: 0
- Requirement traceability: 9/9 must-have covered, 0 missing, 0 deferred (within slice)

---

## Final verdict

**ISSUES.** Three MAJOR findings require parent agent attention before /v5-build:

1. **ISSUE-1** — The test-sweep magnitude is ~5x what the plan estimates. The IMPL_PLAN risks table says "MEDIUM, ≥2 occurrences"; reality is 33 occurrences across 5 test files. Implementer following the plan literally will miss 3 test files entirely.
2. **ISSUE-2** — Scenario 5's "existing test" does not exist. CHECKLIST §4.6 references a phantom test. Either add the test (raising new-test count from 5 to 6) or remove the gate.
3. **ISSUE-3** — Sections §1c and §1d add code specifically for the recreate path, but no test in this slice exercises that path. The defense is untested defensive code.

None of these prevent the feature from shipping if production is post-CASCADE and the implementer is diligent on the sweep. But the plan should be tightened on these points before /v5-build to avoid surprises.

Top issue: **Test-sweep estimate is off by ~5x (33 occurrences vs. plan's "≥2"); implementer will likely miss 3 entire test files (test_pdf_api.py, test_chronological_order.py, test_jobs.py).**
