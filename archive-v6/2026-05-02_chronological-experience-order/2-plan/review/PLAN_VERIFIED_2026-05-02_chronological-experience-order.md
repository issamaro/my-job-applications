---
feature: chronological-experience-order
date: 2026-05-02
status: VERIFIED
reviewer: plan-reviewer
inputs_reviewed:
  - workbench-v6/1-analyze/spec/FEATURE_SPEC_2026-05-02_chronological-experience-order.md
  - workbench-v6/2-plan/design/IMPL_PLAN_2026-05-02_chronological-experience-order.md
  - workbench-v6/1-analyze/ux/UX_DESIGN_2026-05-02_chronological-experience-order.md
  - workbench-v6/2-plan/checks/CHECKLIST_2026-05-02_chronological-experience-order.md
  - source files referenced by the plan (read-only verification)
library_notes: none (plan declared no external docs needed; in-repo references only)
---

# Plan Verification — Chronological Experience Order

## 1. Requirement traceability

| requirement (FEATURE_SPEC "Scope IN") | covered_by (IMPL_PLAN) | status |
|---|---|---|
| 1. Remove "Reorder work experiences by relevance" from `services/llm/base.py` (SYSTEM_PROMPT and USER_PROMPT_TEMPLATE) | File 1 (`services/llm/base.py`) — strikes L49 and L124 | covered |
| 2. After LLM returns work experiences, sort by `start_date` desc in `services/resume_generator.py` before persisting | File 2 — adds module-level `read_experiences_chronologically()` and call site after L66 | covered |
| 3. Add drag-and-drop reorder UI to Work Experience section of `src/components/ResumeView.svelte`; persist via existing `updateResume` | File 3 — markup, state, four handlers, CSS | covered |
| 4. Reorder must persist across reloads (auto, since save rewrites array) | Implicit via #3 (save uses `updateResume(resume.id, resumeData)` with array index as source of truth) | covered |
| Success criterion: automated test that `generate(...)` returns chronological order | File 4 Test 1 (`test_generate_sorts_work_experiences_chronological`) | covered |
| Success criterion: automated test that prompts no longer contain reorder line | File 4 Test 4 (`test_llm_prompts_no_relevance_reorder`) | covered |
| BDD Scenario 1 — generation produces chronological order | Test 1 | covered |
| BDD Scenario 2 — drag-drop persists | manual (resume editor) row in test plan | covered (manual) |
| BDD Scenario 3 — included=false items don't appear | not directly retested by plan; relies on existing `PdfPreview` filter (acknowledged in "Files NOT touched") | covered (existing behavior, no regression risk asserted) |
| BDD Scenario 4 — current position (end_date null) sorts by start_date | Test 2 (`test_generate_handles_ongoing_jobs_by_start_date`) | covered |

No "Should Have" list exists in this spec. Scope OUT items are confirmed not addressed (correctly).

**Total**: 4/4 must-have items covered; 4/4 success criteria covered; 4/4 BDD scenarios covered (one indirectly via existing behavior).

## 2. File-path verification

| reference | type | exists | status |
|---|---|---|---|
| `services/llm/base.py` | modify | yes (128 lines) | OK |
| `services/llm/base.py:49` line `- Reorder work experiences by relevance...` | modify | yes (`grep -n` matches L49) | OK |
| `services/llm/base.py:124` line `- Reorder work experiences by relevance...` | modify | yes (`grep -n` matches L124) | OK |
| `services/llm/base.py::SYSTEM_PROMPT` constant | modify | yes (defined at L40) | OK |
| `services/llm/base.py::USER_PROMPT_TEMPLATE` constant | modify | yes (defined at L54) | OK |
| `services/resume_generator.py` | modify | yes (221 lines) | OK |
| `services/resume_generator.py::generate()` (claimed L23, body L65-105) | modify | yes (`def generate` at L23; `resume_content = llm_result.get("resume", {})` at L66) | OK |
| `services/resume_generator.py::llm_service.analyze_and_generate` call | reference | yes (L45) | OK |
| `services/resume_generator.py::read_experiences_chronologically` (new symbol) | create | parent file exists; symbol new — OK | OK |
| `schemas.py` (cited :228-237 for `ResumeWorkExperience`, :58-65 for validator) | reference | yes; `ResumeWorkExperience` at L228-237; `WorkExperienceCreate` validator at L58-65 (verified `r"^\d{4}-(0[1-9]\|1[0-2])$"`) | OK |
| `src/components/ResumeView.svelte` | modify | yes (657 lines) | OK |
| `src/components/ResumeView.svelte:259-305` `<ResumeSection title={labels.workExperience}>` block | modify | yes (`<ResumeSection title={labels.workExperience}>` at L259-260; closes at L305) | OK |
| `src/components/ResumeView.svelte:266-302` `{#each resumeData.work_experiences}` | modify | yes (each at L266; closes at L302) | OK |
| `src/components/ResumeView.svelte:69-73` `$effect` cloning `resume.resume` into `resumeData` | reference | yes (verified verbatim) | OK |
| `src/components/ResumeView.svelte::updateResume` import | reference | yes (L7: `import { updateResume, downloadPdf } from '../lib/api.js'`) | OK |
| `src/components/ResumeView.svelte::editingId`, `editValue`, `saving`, `toastType`, `toastMessage` state vars | reference | yes (L58, L59, L60, L66, L67) | OK |
| `src/components/Languages.svelte` (cited :127-164 handlers, :235-254 markup, :315-341 CSS) | reference | yes (341 lines; handlers L127-164, markup L235-254, CSS L315-341 — all match exactly) | OK |
| `src/components/Languages.svelte:246` `aria-label="Drag to reorder"` | reference | yes (L246) | OK |
| `tests/test_resume_generator.py:67-95` `@patch("services.resume_generator.llm_service.analyze_and_generate")` | reference | yes (`@patch` at L67; test body L67-95 verified) | OK |
| `tests/test_llm_language.py:1-52` imports `USER_PROMPT_TEMPLATE`, asserts substrings | reference | yes (file is exactly 52 lines; import at L4) | OK |
| `tests/test_chronological_order.py` (new file) | create | parent dir `tests/` exists | OK |

No hallucinated files. No hallucinated symbols.

## 3. Library-pattern verification

The plan explicitly skipped external docs research, citing in-repo references as authoritative.

| pattern | documented_in | status |
|---|---|---|
| Svelte 5 `$state(null)` for `draggedIndex` | `Languages.svelte:24` (verified) | OK |
| `ondragstart`/`ondragover`/`ondrop`/`ondragend` event attributes | `Languages.svelte:239-242` (verified) | OK |
| `draggable="true"` boolean attribute | `Languages.svelte:238` (verified) | OK |
| Splice-and-reassign array reorder pattern (`newItems.splice(...); items = newItems`) | `Languages.svelte:136-141` (verified) | OK |
| `$effect` re-clone fallback on error (revert via `resumeData = JSON.parse(JSON.stringify(resume.resume))`) | `ResumeView.svelte:69-73` (verified pattern; reuses prop) | OK |
| Python `sorted(iterable, key=..., reverse=True)` with stdlib | stdlib (no docs needed) | OK |
| FastAPI test pattern `@patch("services.resume_generator.llm_service.analyze_and_generate")` | `tests/test_resume_generator.py:67` and 5 other call sites | OK |
| Prompt-string substring assertion (`"..." in PROMPT_CONST`) | `tests/test_llm_language.py` (e.g. L33, L37, L41) | OK |

No deprecated APIs used. No undocumented patterns.

## 4. Checklist coverage

| plan_file | checklist_items | status |
|---|---|---|
| File 1 (`services/llm/base.py`) | Section 2 items removing the line at L49 and L124 (2 checks) | covered |
| File 2 (`services/resume_generator.py`) | Section 2 items for `sorted()` lambda, module-level fn placement, call site (3 checks) | covered |
| File 3 (`src/components/ResumeView.svelte`) | Section 2 (state, 4 functions, draggable attr, class:dragging, drag-handle markup — 8 checks) + Section 3 UX (5 checks) + Section 5 a11y (4 checks) | covered |
| File 4 (`tests/test_chronological_order.py`) | Section 4 — 4 test checks, one per planned test | covered |

**Orphan checks**: Section 0 (Ecosystem) and Section 1 (Dependencies) are derived from `pyproject.toml` and `package.json`, not directly from IMPL_PLAN, but the checklist explicitly traces each to the plan's library/framework table. Acceptable — these are environment preconditions, not orphaned.

## 5. Risks and ambiguities

| # | finding | location | severity |
|---|---|---|---|
| F1 | Plan justifies sort-key safety with "YYYY-MM enforced at input by `WorkExperienceCreate.start_date` validator" but the data being sorted comes from the LLM JSON output (raw dict via `resume_content["work_experiences"]`), NOT from `WorkExperienceCreate`. The actual safety net is "the prompt examples show YYYY-MM" + the `or ""` fallback for missing keys. The plan acknowledges this in R3, but the F2/L2 narrative still leans on the wrong validator. The fallback works regardless, so this is a documentation accuracy issue rather than a correctness bug. | IMPL_PLAN.md File 2 sort-key bullet, contradicts R3 in same file | MINOR |
| F2 | "Mirroring" claim about Languages.svelte's inline-edit suppression is imprecise. Languages uses an outer `{#if showForm}...{:else}<div draggable="true">...{/if}` that **swaps the parent DOM node**. The plan instead keeps the same `<div class="work-item">` and toggles `draggable={editingId !== exp.id}` — a different mechanism. Both work, but the comparison is misleading. Implementer may waste time looking for the matching pattern. | IMPL_PLAN.md File 3 Risk paragraph & UX_DESIGN.md "State: edit mode active" | MINOR |
| F3 | Lean-code naming reasoning wavers visibly: the plan first reasons "sort is closest to `update`" then immediately switches to "Best fit: rename to `read_experiences_chronologically`". The choice between `update_*` and `read_*` is essentially aesthetic — neither maps cleanly to the nine permitted verbs. Result is OK but the deliberation signals the lean-code spec doesn't fit transformations (sort) cleanly. Not actionable for the build phase. | IMPL_PLAN.md File 2 "Lean-code naming" paragraph | MINOR |
| F4 | Lean-code rename for drag handlers (`writeReorderedOrder`, `deleteDraggedIndex`) is internally consistent but **stylistically awkward** — `writeReorderedOrder` has "Order" twice; `deleteDraggedIndex` reads as deleting the index from a database. The plan acknowledges this awkwardness implicitly ("Honest assessment: HTML5 drag-drop event handlers are intrinsically 'handle X event' callbacks"). Not blocking but the implementer should be free to revise during build. | IMPL_PLAN.md File 3 "Lean-code rules" paragraph | MINOR |
| F5 | The plan's drop-error revert path has a subtle ordering: it sets `resumeData = JSON.parse(JSON.stringify(resume.resume))`, but if the user has unrelated unsaved edits in flight (e.g. an inline description edit not yet saved), the revert clobbers them. The plan doesn't discuss this interaction. In practice, `editingId` likely prevents drag during edit (per the conditional `draggable`), but a savedId-but-not-yet-toast'd edit could still race. Low likelihood, real surface. | IMPL_PLAN.md File 3 `handleDrop`/`writeReorderedOrder` revert logic | MINOR |
| F6 | Vague terms found: "as needed" / "may" / "etc." are absent from IMPL_PLAN (good). One vague term: "Even simpler: copy Languages.svelte's loadData() pattern by exposing a refresh path. Decision: on error, set toast + revert from `resume.resume`" — the alternative ("Even simpler: copy...") is left undecided in the prose despite the "Decision" label. Implementer should ignore the alternative. | IMPL_PLAN.md File 3, drop handler description | MINOR |
| F7 | The plan does not address what happens if the LLM returns work experiences with **identical** `start_date` values (collision case). `sorted()` with `reverse=True` is stable, so original (LLM-emitted) order is preserved among ties — but this isn't asserted by any test or comment. No BDD scenario covers it. Likely acceptable in practice (most real CVs don't have two jobs starting the same month) but is an unaddressed edge. | IMPL_PLAN.md File 2; FEATURE_SPEC scenarios | MINOR |
| F8 | No concurrency / race-condition analysis for the drop persist flow. If the user drops twice rapidly while a previous `updateResume` is in-flight, both `await` calls run concurrently, and the second resolves with a stale `resumeData` reference (now overwritten). This matches Languages.svelte's behavior (also no guard), so it's pattern-consistent — but worth noting. | IMPL_PLAN.md File 3 R1; not raised | MINOR |
| F9 | No database migration discussion needed (correct — JSON column, array order). No new error scenarios introduced for FEATURE_SPEC's BDD. No unbounded loops. | n/a | none |

No BLOCKER findings. No MAJOR findings.

## Final verdict

**VERIFIED** — every file path verified to exist; every cited line number confirmed verbatim; every cited symbol confirmed; every must-have requirement traced to a plan section; every plan file traced to checklist coverage. Risks are MINOR documentation/aesthetic concerns, not correctness bugs.

The plan author was careful with line numbers — every `:NNN-MMM` reference matched the actual repo content exactly, including the load-bearing claim that `ResumeWorkExperience.start_date` has no inline validator (R3) and the load-bearing claim about Languages.svelte's three line ranges. The lean-code naming wrestling is visible in the prose but the final decisions are internally consistent with the spec.

The only substantive gap is documentation accuracy around where format validation actually happens (F1) — the validator on `WorkExperienceCreate` doesn't actually protect the LLM-output dict path. The runtime safety comes from `or ""` fallback + LLM following the prompt example. Correctness preserved.
