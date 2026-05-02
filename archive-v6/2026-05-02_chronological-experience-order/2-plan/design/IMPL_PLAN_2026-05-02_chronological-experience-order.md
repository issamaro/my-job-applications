---
slug: chronological-experience-order
date: 2026-05-02
ceremony_level: M
phase: plan
artifact: impl-plan
---

# Implementation Plan — Chronological Experience Order

## Library / framework research

**No external docs needed for this feature.** The change touches three areas — Python stdlib (`sorted()`), Svelte 5 HTML5 drag-drop, and pytest. All have authoritative in-repo references that are more accurate than docs would be:

| area | in-repo reference |
|---|---|
| Svelte 5 drag-drop | `src/components/Languages.svelte:127-164` (handlers) and `:235-254` (markup) and `:315-341` (CSS). Uses Svelte 5 runes (`$state`, `$effect`) — exact pattern this feature reuses. |
| Server-side sort + Pydantic | `services/resume_generator.py:65-105` (the `generate()` flow) + `schemas.py:228-237` (`ResumeWorkExperience`). |
| FastAPI test pattern | `tests/test_resume_generator.py:67-95` (`@patch("services.resume_generator.llm_service.analyze_and_generate")`). |
| Prompt-string assertion | `tests/test_llm_language.py:1-52` (imports `USER_PROMPT_TEMPLATE`, `assert "..." in prompt`). |

Stack-resolver and parallel docs-researcher are skipped — no new dependencies, no version-sensitive APIs touched. plan-reviewer can flag if disagrees.

## Files to modify

### File 1 — `services/llm/base.py`
- **Change**: Remove the line `- Reorder work experiences by relevance (most relevant first)` at L49 (in `SYSTEM_PROMPT`'s Guidelines block) and L124 (in `USER_PROMPT_TEMPLATE`'s Important block).
- **Symbols touched**: `SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE` (both module-level constants).
- **Risk**: minimal. Removing a single bullet leaves the surrounding list valid. The "Keep the original IDs from the profile" line below remains.
- **Lean-code rules**: file already has a docstring at the top, not the lean-code two-line header. We honor existing project convention (the LEAN-CODE rules apply to *new* code; surgical edits to existing files preserve their pre-existing header style — see `CLAUDE.md` "Adapt the file header format to your project's existing license/header conventions").

### File 2 — `services/resume_generator.py`
- **Change**: In `generate()` (around L65-97), after `resume_content = llm_result.get("resume", {})` and BEFORE the JSON-serialize+INSERT, sort the work_experiences list by `start_date` descending. Add a new helper function `sort_work_experiences_chronologically(experiences: list[dict]) -> list[dict]`.
- **Why a helper**: it's testable in isolation and the sort is its own operation — fits one-function-one-job. Place it as a module-level function (not a method) inside `services/resume_generator.py`, above the class.
- **Sort key**: `start_date` (lexicographic descending = chronological descending because YYYY-MM is enforced at input by `WorkExperienceCreate.start_date` validator at `schemas.py:58-65`).
- **Missing-data handling**: if `start_date` is missing/None on a dict (LLM glitch), treat as empty string so it sorts last. Single line: `key=lambda we: we.get("start_date") or ""`.
- **Lean-code naming**: `sort_work_experiences_chronologically` — verb is `sort`. Wait — `sort` is not in the permitted nine verbs. The permitted verbs include `update` (modify existing data) and `parse` (transform a format). Sorting is closest to `update` (we're updating the order of an existing list) or could be reframed as `read` (reading-with-sort). Best fit: rename to `read_experiences_chronologically(experiences) -> list` (returns a new list in the desired order). Body: `return sorted(experiences, key=..., reverse=True)`. This frames the operation as "read out a chronological view," which matches what the caller does (assigns the returned list back into `resume_content["work_experiences"]`).
- **Module addition**: a single function, ~5 lines, no class.
- **Caller**: in `generate()`, replace `resume_content = llm_result.get("resume", {})` block with two lines that ensure the sort is applied. Specifically: after line 66 (`resume_content = llm_result.get("resume", {})`), add `resume_content["work_experiences"] = read_experiences_chronologically(resume_content.get("work_experiences", []))`.

### File 3 — `src/components/ResumeView.svelte`
- **Change**: Add drag-drop reorder to the Work Experience list at `:266-302`.
- **State additions** (in `<script>`): `let draggedIndex = $state(null);`
- **Function additions** (model directly on `Languages.svelte:127-164`):
  - `handleDragStart(e, index)` — sets `draggedIndex = index`, `e.dataTransfer.effectAllowed = 'move'`.
  - `handleDragOver(e, index)` — prevents default, reorders the local `resumeData.work_experiences` array in place via splice (mutating Svelte 5 `$state` is fine since we're using `resumeData = JSON.parse(JSON.stringify(...))` clone elsewhere, but for cleanliness do `resumeData.work_experiences = newArray`).
  - `handleDrop(e)` — prevents default, calls `await updateResume(resume.id, resumeData)`. On error, reload via `onBack`+`onRegenerate`? No — there is no `loadData` here. Best fallback: set `toastType = 'error'; toastMessage = 'Could not save order.'` and revert the local array by re-cloning from the original `resume.resume`. Simpler: just show the toast and accept the visual mismatch until the user reloads. Even simpler: copy Languages.svelte's loadData() pattern by exposing a refresh path. Decision: on error, set toast + revert from `resume.resume` (the prop). One-liner: `resumeData = JSON.parse(JSON.stringify(resume.resume));`. This mirrors the `$effect` at L69-73.
  - `handleDragEnd()` — sets `draggedIndex = null`.
- **Markup changes** (around L267-301):
  - On the outer `<div class="work-item">` add: `class:dragging={draggedIndex === index}`, `draggable={editingId !== exp.id}` (boolean attribute — not draggable while editing), `ondragstart={(e) => handleDragStart(e, index)}`, `ondragover={(e) => handleDragOver(e, index)}`, `ondrop={handleDrop}`, `ondragend={handleDragEnd}`.
  - Inside `<div class="work-header">` (currently shows `work-number` + `work-title`), wrap with a `.drag-handle-wrapper` flex container and insert `<span class="drag-handle" aria-label="Drag to reorder">⋮⋮</span>` as the first child.
- **CSS additions** (in the `<style>` block):
  - `.work-item .drag-handle { cursor: grab; color: #999; font-size: 16px; user-select: none; }`
  - `.work-item .drag-handle:active { cursor: grabbing; }`
  - `.work-item.dragging { opacity: 0.5; background: #f0f0f0; }`
  - `.work-item .drag-handle-wrapper { display: flex; align-items: center; gap: 8px; }`
- **Lean-code rules**: file is Svelte (not Python/JS proper). Existing file has no two-line header. We preserve project convention (no header added). Function names use camelCase per project style — `handleDragStart` is **not** lean-compliant (`handle` is forbidden). Rename to `startDrag(e, index)`, `dragOverItem(e, index)`, `dropItem(e)`, `endDrag()`. Wait — `start`, `drag`, `drop`, `end` are not in the permitted nine verbs either. The permitted verbs are: read, write, create, delete, update, find, check, parse, render. Closest fits:
  - `handleDragStart` → `updateDragStart` (begins updating order) — awkward.
  - Honest assessment: HTML5 drag-drop event handlers are intrinsically "handle X event" callbacks. The lean-code spec gives a clear NEVER for `handleX`. Best lean rename: combine intent + verb. `updateDraggedIndex(e, i)`, `updateOrderOnHover(e, i)`, `writeReorderedExperiences(e)`, `updateDraggedIndex()` for end. This preserves the verb-noun pattern.
  - **Decision for plan**: rename per lean-code as `updateDraggedIndex(e, i)` (start), `updateOrderOnHover(e, i)` (over), `writeReorderedOrder(e)` (drop), `updateDraggedIndex()` no-arg (end — wait, that collides). Resolve collision: `clearDraggedIndex()` for end — but `clear` is not permitted; use `delete`. So: `deleteDraggedIndex()`. Final names:
    - `updateDraggedIndex(e, i)` — drag start (writes the index).
    - `updateOrderOnHover(e, i)` — drag over (reorders array as we hover).
    - `writeReorderedOrder(e)` — drop (persists via API).
    - `deleteDraggedIndex()` — drag end (resets state).
  - Implementer note: the existing `Languages.svelte` uses `handleX` names — those are pre-feature legacy. We do not refactor Languages.svelte in this scope. Lean-code rules apply to **new** code only.
- **Risk**: medium. Svelte 5 + drag-drop interaction with the existing inline-edit state machine (`editingId`, `editValue`). Tested mitigation: `draggable={editingId !== exp.id}` ensures dragging is disabled during inline edit.

### File 4 (new) — `tests/test_chronological_order.py`
- **New file** to keep this feature's tests cohesive.
- **Test 1** — `test_generate_sorts_work_experiences_chronological`:
  - Setup: profile via `_setup_profile` style helper (or an inline minimal profile create).
  - Mock `services.resume_generator.llm_service.analyze_and_generate` to return three experiences in shuffled order: A (2020-01), B (2024-06), C (2022-03).
  - POST `/api/resumes/generate`.
  - Assert response `resume.work_experiences[*].start_date` equals `["2024-06", "2022-03", "2020-01"]`.
- **Test 2** — `test_generate_handles_ongoing_jobs_by_start_date`:
  - LLM returns: P (start_date=2024-01, end_date=None), Q (start_date=2023-06, end_date=2024-12).
  - Assert order is P, Q. Locks the contract that `start_date` alone is the sort key (no end_date tiebreak).
- **Test 3** — `test_generate_handles_two_ongoing_jobs`:
  - Edge case from analysis-reviewer's nit #1.
  - LLM returns: R (start_date=2024-03, end_date=None), S (start_date=2024-08, end_date=None).
  - Assert order is S, R (later start wins; both ongoing).
- **Test 4** — `test_llm_prompts_no_relevance_reorder`:
  - Imports `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` from `services.llm.base`.
  - `assert "Reorder work experiences by relevance" not in SYSTEM_PROMPT`.
  - `assert "Reorder work experiences by relevance" not in USER_PROMPT_TEMPLATE`.
- **Lean-code rules** apply: header lines, no inline comments (test names are self-documenting), verb prefixes (`test_generate_*`, `test_llm_*` — `test` is the framework's verb, exempt by convention as in all existing test files in this repo). Following existing test-file style — no LEAN-CODE header, since `tests/test_llm_language.py` and others use only a docstring. **Decision**: match existing test-file style (docstring header, no two-line LEAN-CODE block) for consistency with the rest of the test suite.

## Files NOT touched (explicit out-of-scope)

- `src/components/WorkExperience.svelte` — profile-side editor, not the resume view.
- `src/components/PdfPreview.svelte` — already filters `included !== false` correctly. No change.
- `services/pdf_generator.py` — receives `work_experiences` array in display order; no logic change needed.
- `routes/resumes.py` — existing `PUT /api/resumes/{id}` is sufficient for drag-drop persistence (pass-through to `update_resume`).
- `database.py` / migrations — no schema change. The resume_content JSON's array order is the source of truth.

## Test plan

| layer | test file | what it verifies |
|---|---|---|
| unit | `tests/test_chronological_order.py::test_generate_sorts_work_experiences_chronological` | server-side sort applied to LLM output |
| unit | `tests/test_chronological_order.py::test_generate_handles_ongoing_jobs_by_start_date` | end_date does not factor in |
| unit | `tests/test_chronological_order.py::test_generate_handles_two_ongoing_jobs` | two ongoing jobs sort by start_date |
| unit | `tests/test_chronological_order.py::test_llm_prompts_no_relevance_reorder` | regression-lock that the prompt strings stay clean |
| manual (inspector) | resume editor | drag-drop reorders + persists; numbering updates live; edit-mode disables drag |

## Risks

- **R1** — Svelte 5 drag-drop event timing: `ondragover` fires repeatedly; if we `await updateResume` here we'd thrash the API. Mitigation: persist on `ondrop` only. (Pattern already validated in Languages.svelte.)
- **R2** — Mid-drag visual glitch when mutating `resumeData.work_experiences = newArray`: Svelte 5 `$state` reactivity might require a fresh array reference. Mitigation: always assign a new array (Languages.svelte does `items = newItems` — same pattern).
- **R3** — Sort assumption that `start_date` is YYYY-MM: locked by `schemas.py:58-65` validator on the profile-side input, but `ResumeWorkExperience.start_date` itself has no inline format validator (analysis-reviewer's nit #3). Mitigation: a single comment line in `read_experiences_chronologically` documenting the assumption is allowed by lean-code (the WHY is non-obvious — it's a hidden invariant from a different file). Or, more lean-code compliant: name the function precisely so the assumption is in the name. The current name `read_experiences_chronologically` already implies date-based ordering; the YYYY-MM assumption is project-wide. **Decision**: no comment; rely on the test (`test_generate_sorts_work_experiences_chronological`) as the lock.
- **R4** — Drag-drop accessibility: keyboard reorder is out of scope. The drag handle is a `<span>` (not focusable), matching Languages.svelte. Documented in UX_DESIGN.

## Build sequence (the order to apply changes)

1. Add `read_experiences_chronologically` helper + call site in `services/resume_generator.py` (smallest, isolated).
2. Remove the two prompt lines in `services/llm/base.py`.
3. Write `tests/test_chronological_order.py`. Run tests — should pass for tests 1-4.
4. Add drag-drop to `src/components/ResumeView.svelte`. Manual browser test.
5. Re-run full test suite.

This sequence makes server-side changes (testable without browser) before frontend changes (manual-test-only).
