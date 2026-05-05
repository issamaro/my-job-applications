# PLAN_VERIFIED — llm-keeps-all-experiences

feature: llm-keeps-all-experiences
date: 2026-05-05
status: ISSUES
reviewer: plan-reviewer
ceremony_level: S
inputs_reviewed:
- backlog/refined/llm-keeps-all-experiences.md (used in lieu of FEATURE_SPEC for ceremony S)
- workbench-v6/2-plan/design/IMPL_PLAN_2026-05-05_llm-keeps-all-experiences.md
- workbench-v6/2-plan/checklist/CHECKLIST_2026-05-05_llm-keeps-all-experiences.md (NOT PRESENT — concurrent build, skipped per instructions)

## 1. Traceability table

| Acceptance criterion (refined backlog) | Covered by (IMPL_PLAN section) | Status |
|---|---|---|
| Length of `resume.work_experiences` equals input profile work-experience count, every entry has `included=true`, regardless of relevance | `services/resume_generator.py` post-LLM guard `create_all_experiences_list` (lines 30-58) | covered |
| LLM still tailors `description` and provides `match_reasons` for every experience (empty allowed) | `services/llm/base.py` prompt edits (lines 17-28) | covered |
| Adjust downstream code/default that depends on LLM picking inclusion | Risks section confirms `pdf_generator.py` defaults to `True`; no other downstream code identified | covered |
| Automated test in `tests/test_resume_prompts.py` asserting prompt encodes the rule | `tests/test_resume_prompts.py` two new tests (lines 59-62) | covered |
| Automated test on a fixture where ≥1 experience is irrelevant: result has all experiences with `included=true` | `tests/test_resume_generator.py` three new integration tests (lines 64-71) | covered |
| BDD: 4 profile experiences + job matching only 2 → resume has 4 with `included=true` | `test_generate_returns_all_work_experiences_even_if_llm_drops_one` | covered |
| BDD: experience with no overlap → `match_reasons` may be empty but `included=true` | Implicit in the integration tests; not asserted explicitly that `match_reasons==[]` *despite* irrelevance — only that fallback experiences come back with `match_reasons=[]` | partially covered (see MAJOR-1) |

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `services/llm/base.py` | modify | yes | OK |
| `services/llm/base.py:USER_PROMPT_TEMPLATE` | modify | yes (line 63) | OK |
| `services/llm/base.py:SYSTEM_PROMPT` | not modified (plan says no change needed) | yes (line 40) | OK |
| `services/llm/base.py:Only include profile items that are relevant to this job` | replace | yes (line 132) | OK |
| `services/llm/base.py:For each included work experience, explain why it matches (match_reasons)` | replace | yes (line 133) | OK |
| `services/llm/base.py:Set included=false for items that are not relevant` | replace | yes (line 136) | OK |
| `services/resume_generator.py` | modify | yes | OK |
| `services/resume_generator.py:ResumeGeneratorService.generate` | modify | yes (line 27) | OK |
| `services/resume_generator.py:read_experiences_chronologically` | reference (no change) | yes (line 22) | OK |
| `services/resume_generator.py:llm_service.analyze_and_generate` | reference | yes (line 49) | OK |
| `tests/test_resume_prompts.py` | modify | yes | OK |
| `tests/test_resume_generator.py` | modify | yes | OK |
| `tests/test_resume_generator.py:_setup_profile` | reference | yes (line 5) | OK |
| `services/pdf_generator.py:exp.get("included", True)` | reference (risks section) | yes (line 60) | OK |

No hallucinated paths. No hallucinated symbols.

## 3. Library-pattern verification

No new libraries introduced. `Libraries` section explicitly states "No new libraries. No parallel research dispatch (light plan, libs == 0)." Nothing to verify.

## 4. Checklist coverage

CHECKLIST file is being built concurrently and was not present at review time. Per reviewer instructions, checklist cross-checks were skipped. The IMPL_PLAN's own internal `Test plan` section (lines 80-88) provides interim coverage:
- 2 prompt tests in `test_resume_prompts.py`
- 3 integration tests in `test_resume_generator.py`
- Regression-pass requirement on existing prompt/generator/chronological tests
- 1 manual inspect-phase verification

Once the CHECKLIST is produced the parent agent should re-run the orphan/coverage check before /v5-build.

## 5. Risks and ambiguities

### MAJOR-1 — Existing generator tests will silently change behavior, no regression test guards them
Location: `tests/test_resume_generator.py`, 7 occurrences of `"work_experiences": []` mocked LLM responses (lines 79, 112, 146, 164, 190, 237, 299) while `_setup_profile` (line 14-22) creates 1 real work experience.
After the new guard, every one of those 7 tests will receive a result with 1 work experience (the profile-fallback one), not 0. None of those tests asserts `len(work_experiences) == 0`, so they will not fail — but the plan does NOT flag this hidden behavior change. If any future test reads `resume["work_experiences"][0]` expecting LLM-tailored content, it would receive profile-original content and silently misassert. The plan should at minimum (a) acknowledge this in Risks, and (b) decide whether existing mock fixtures need to be updated to include the profile experience, OR add a regression assertion in one existing test that the count is now 1.
Severity: MAJOR.

### MAJOR-2 — `id` matching is fragile and the documented fallback is "not in scope for v1"
Location: IMPL_PLAN line 77 (Risks).
The plan: "if the LLM omits `id`, fall back to matching by `(company, title, start_date)` triple. Not in scope for v1; the prompt already says 'Keep the original IDs'." But the prompt is best-effort (the very justification for the guard). If the LLM drops `id` on one of the 2 returned experiences, that experience falls into the "dropped by LLM" branch and is replaced by profile-original content — the user silently loses LLM tailoring on that experience without any signal. This contradicts the success criterion "LLM still tailors description". The plan should either (a) implement the triple-key fallback, or (b) explicitly accept that LLM-without-id-experiences are treated as dropped, with a test that pins the behavior.
Severity: MAJOR.

### MAJOR-3 — The acceptance test for "irrelevant experience returns empty match_reasons but included=true" is not explicit
Location: refined backlog line 30 (BDD scenario 2) vs IMPL_PLAN lines 64-69.
The three integration tests cover (1) all 4 returned, (2) LLM descriptions kept for the 2 LLM-returned, (3) profile descriptions for the 2 dropped. Scenario 2 of the BDD says: an experience with NO OVERLAP, when the LLM RETURNS the tailored resume, then `match_reasons` may be empty but `included=true`. The plan's integration tests cover the fallback case (LLM dropped the experience) but do not cover the case where the LLM RETURNS the experience with empty `match_reasons` and the guard preserves that empty list while keeping `included=true`. Add a fourth assertion or test for this subcase.
Severity: MAJOR.

### MINOR-1 — Plan contains stream-of-consciousness naming derivation in the artifact
Location: IMPL_PLAN line 49 ("verb prefix `merge` is not in the canonical nine. Use `read_all_experiences_with_llm` instead — wait, that's also wrong, ..."). The final name `create_all_experiences_list` complies with CLAUDE.md (verb=`create`, three words after, no abbreviations). However, leaving the abandoned candidates and "wait, that's also wrong" in the published plan is unusual — implementer may misread which name is final. Recommend the final IMPL_PLAN state only the chosen name.
Severity: MINOR.

### MINOR-2 — Vague phrase "near it" in the prompt-text assertion
Location: IMPL_PLAN line 61 (`asserts the user prompt contains a phrase like "return ALL profile work_experiences" AND "included=true" near it`). "Near it" has no operationalization — the implementer may write `assert phrase_a in prompt and phrase_b in prompt` (which does NOT verify proximity), and the test will pass even if the two phrases live in completely separate paragraphs. Either drop the "near" requirement, or specify a concrete distance/single-line check.
Severity: MINOR.

### MINOR-3 — No explicit statement that the `id` field's type contract is preserved
Location: IMPL_PLAN line 43 (`llm_by_id = {exp["id"]: exp for exp in llm_experiences if "id" in exp}`).
Profile work-experience `id` is an integer from the SQLite `INTEGER PRIMARY KEY`. The LLM may return `id` as a string (it returns JSON). Dict lookup will silently fail and the experience will be classified as dropped. The plan should either (a) coerce `int(exp["id"])` defensively, or (b) note that the prompt example uses unquoted integers and trust schema validation. Currently unaddressed.
Severity: MINOR.

### MINOR-4 — `order` field handling is hand-waved as "acceptable"
Location: IMPL_PLAN line 76 (Risks: "Acceptable — `order` is not a primary contract.").
The fallback uses `order=0` for restored experiences (line 46). After `read_experiences_chronologically` re-sorts, the order field is overwritten or ignored anyway, so this is likely fine. Worth confirming that the persisted `order` in the DB doesn't get exposed elsewhere with the wrong value (e.g., editor drag-and-drop might rely on it).
Severity: MINOR.

### MINOR-5 — Vague terms scan
Located: searched IMPL_PLAN for "appropriate", "robust", "as needed", "etc.", "and so on", "iterate until", "keep adjusting" — none found. Clean on this dimension.

## 6. Lean-code naming check (CLAUDE.md)

Function `create_all_experiences_list(profile_experiences, llm_experiences)`:
- Verb prefix: `create` — one of the nine permitted verbs ✓
- Words after verb: `all`, `experiences`, `list` = exactly 3 ✓
- No abbreviations ✓
- No framework suffix ✓
- One job: builds the merged canonical list (does not also write or render) ✓

The naming complies with CLAUDE.md. The internal "wait, that's also wrong" derivation in line 49 is documentation noise (MINOR-1) but the chosen name itself is valid.

Parameter names `profile_experiences`, `llm_experiences` are spelled out (no abbreviations) ✓.

## 7. Scope drift check (refined Scope IN vs IMPL_PLAN deliverables)

Refined Scope IN:
1. Update tailored-resume prompt in `services/llm/base.py` so model never sets `included=false` on `work_experiences[*]` → IMPL_PLAN delivers (lines 17-28).
2. LLM still tailors `description` and provides `match_reasons` → IMPL_PLAN preserves (no prompt changes to those instructions).
3. Adjust downstream code/default → IMPL_PLAN adds the post-LLM guard. This goes BEYOND the refined backlog's "Adjust ... post-processing" — the backlog could be read as "if anything currently *forces* included=false, change it"; IMPL_PLAN adds a defensive guard that overrides whatever the LLM returns. This is broader than necessary if you trust the prompt, but is justified by the plan's "the prompt is best-effort; the guard is the actual contract" — and the BDD test in the backlog implicitly demands the guard, since otherwise a non-deterministic LLM could regress the test. Verdict: NOT scope drift; this is the correct interpretation.
4. Update or add tests → IMPL_PLAN delivers.

Refined Scope OUT (plan must NOT touch):
- UI changes to resume editor → IMPL_PLAN does not touch UI ✓
- Inclusion logic for skills/education/projects → IMPL_PLAN explicitly preserves ✓
- match_score / job_analysis → IMPL_PLAN does not touch ✓
- Description tailoring → IMPL_PLAN preserves ✓

No scope drift detected.

## 8. Risks the plan missed

- **Existing-test silent behavior shift** (covered above as MAJOR-1) — 7 mocked-empty tests now return 1 experience.
- **LLM `id` type coercion** (covered as MINOR-3) — JSON int vs string lookup mismatch.
- **No-id LLM fallback** (covered as MAJOR-2) — guard treats no-id LLM experiences as dropped, silently losing tailoring.
- **`match_reasons` shape contract**: plan says "ensure `match_reasons` exists (default `[]`)". If the LLM returns `match_reasons` as a string ("Python, Team Leadership") instead of a list, the guard will pass it through unchanged, and the schema validator downstream will reject the resume. Not addressed — plan assumes LLM returns the right shape.
- **Order of operations**: the plan says "BEFORE the chronological sort" (line 56). Verified: `read_experiences_chronologically` runs at line 71 of resume_generator.py. The plan correctly identifies the insertion point.

## 9. Final verdict

**ISSUES** — three MAJOR findings (MAJOR-1, MAJOR-2, MAJOR-3) need parent-agent decisions before /v5-build:

- MAJOR-1: silent regression in 7 existing tests due to behavior change
- MAJOR-2: id-omitted LLM experiences silently lose tailoring; v1-out-of-scope without a test pinning the chosen behavior
- MAJOR-3: BDD scenario 2 (LLM returns experience with empty match_reasons) is not explicitly tested

The plan is otherwise structurally sound: file paths and symbols all verify, no scope drift, no hallucinations, lean-code naming compliant, no new libraries.

---

## Return value

```
status: ISSUES
artifact: /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench-v6/2-plan/verify/PLAN_VERIFIED_2026-05-05_llm-keeps-all-experiences.md
traceability: covered=6/7, missing=0, deferred=0, partial=1
hallucinated_files: 0
hallucinated_symbols: 0
checklist_orphans: skipped (concurrent build)
risk_findings: blockers=0, major=3, minor=5
top_issue: 7 existing test fixtures mock "work_experiences: []" but _setup_profile creates 1 real experience — new guard silently changes their result count from 0 to 1 with no regression assertion.
```
