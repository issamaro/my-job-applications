---
feature: chronological-experience-order
date: 2026-05-02
total_checkboxes: 28
derived_from:
  - IMPL_PLAN_2026-05-02_chronological-experience-order.md
  - UX_DESIGN_2026-05-02_chronological-experience-order.md
  - FEATURE_SPEC_2026-05-02_chronological-experience-order.md
  - .python-version
  - pyproject.toml
  - package.json
---

# Checklist — Chronological Experience Order

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Library / framework research" table, pyproject.toml `requires-python = ">=3.13"`
- [ ] Virtual environment created and activated  → source: pyproject.toml `[tool.uv]` — project uses uv

---

## Section 1 — Dependencies

No library_notes_paths were provided. The plan explicitly states no new dependencies are introduced and all libraries referenced are already in-repo. Checks below are derived from the plan's in-repo references cross-referenced against pyproject.toml and package.json.

- [ ] `fastapi>=0.100.0` present in `pyproject.toml`  (verify: `uv tree --package fastapi`)  → source: IMPL_PLAN "Files NOT touched" — `routes/resumes.py` uses FastAPI; existing dependency
- [ ] `pydantic>=2.0` present in `pyproject.toml`  (verify: `uv tree --package pydantic`)  → source: IMPL_PLAN File 2 — "Pydantic" listed in the library/framework table; `schemas.py` uses Pydantic validators
- [ ] `pytest>=8.0.0` present in `pyproject.toml` dev dependencies  (verify: `uv tree --package pytest`)  → source: IMPL_PLAN File 4 — `tests/test_chronological_order.py` uses pytest
- [ ] `pytest-asyncio>=0.24.0` present in `pyproject.toml` dev dependencies  (verify: `uv tree --package pytest-asyncio`)  → source: IMPL_PLAN File 4 — existing test files use `@pytest.mark.asyncio` pattern
- [ ] `httpx>=0.27.0` present in `pyproject.toml` dev dependencies  (verify: `uv tree --package httpx`)  → source: IMPL_PLAN File 4 — test posts to `/api/resumes/generate`; existing test pattern uses httpx TestClient
- [ ] `svelte^5.0.0` present in `package.json`  (verify: `npm list svelte`)  → source: IMPL_PLAN File 3 — "Svelte 5 runes (`$state`, `$effect`) — exact pattern this feature reuses"

---

## Section 2 — Syntax

- [ ] `sorted()` with `key=lambda we: we.get("start_date") or ""` and `reverse=True` used in `services/resume_generator.py` inside `read_experiences_chronologically`  → source: IMPL_PLAN File 2 — "Sort key: `start_date` (lexicographic descending)…Missing-data handling: `key=lambda we: we.get("start_date") or ""`"
- [ ] `read_experiences_chronologically` is a module-level function (not a method) placed above the class in `services/resume_generator.py`  → source: IMPL_PLAN File 2 — "Place it as a module-level function (not a method) inside `services/resume_generator.py`, above the class"
- [ ] `resume_content["work_experiences"] = read_experiences_chronologically(resume_content.get("work_experiences", []))` appears in `generate()` after the `llm_result.get("resume", {})` line  → source: IMPL_PLAN File 2 — "after line 66 (`resume_content = llm_result.get("resume", {})`), add…"
- [ ] Line `- Reorder work experiences by relevance (most relevant first)` removed from `SYSTEM_PROMPT` in `services/llm/base.py` (was L49)  → source: IMPL_PLAN File 1 — "Remove the line `- Reorder work experiences by relevance (most relevant first)` at L49 (in `SYSTEM_PROMPT`'s Guidelines block)"
- [ ] Line `- Reorder work experiences by relevance (most relevant first)` removed from `USER_PROMPT_TEMPLATE` in `services/llm/base.py` (was L124)  → source: IMPL_PLAN File 1 — "and L124 (in `USER_PROMPT_TEMPLATE`'s Important block)"
- [ ] `let draggedIndex = $state(null)` declared in `<script>` of `src/components/ResumeView.svelte`  → source: IMPL_PLAN File 3 — "State additions (in `<script>`): `let draggedIndex = $state(null);`"
- [ ] `updateDraggedIndex(e, i)` function present in `src/components/ResumeView.svelte` (sets `draggedIndex = i`, `e.dataTransfer.effectAllowed = 'move'`)  → source: IMPL_PLAN File 3 — "Final names: `updateDraggedIndex(e, i)` — drag start (writes the index)"
- [ ] `updateOrderOnHover(e, i)` function present in `src/components/ResumeView.svelte` (prevents default, reorders `resumeData.work_experiences` via new array assignment)  → source: IMPL_PLAN File 3 — "`updateOrderOnHover(e, i)` — drag over (reorders array as we hover)"
- [ ] `writeReorderedOrder(e)` function present in `src/components/ResumeView.svelte` (prevents default, calls `await updateResume(resume.id, resumeData)`, on error sets toast and reverts from `resume.resume`)  → source: IMPL_PLAN File 3 — "`writeReorderedOrder(e)` — drop (persists via API)" and revert logic
- [ ] `deleteDraggedIndex()` function present in `src/components/ResumeView.svelte` (sets `draggedIndex = null`)  → source: IMPL_PLAN File 3 — "`deleteDraggedIndex()` — drag end (resets state)"
- [ ] `draggable={editingId !== exp.id}` attribute set on `<div class="work-item">` in `src/components/ResumeView.svelte`  → source: IMPL_PLAN File 3 — "`draggable={editingId !== exp.id}` (boolean attribute — not draggable while editing)"
- [ ] `class:dragging={draggedIndex === index}` applied to `<div class="work-item">` in `src/components/ResumeView.svelte`  → source: IMPL_PLAN File 3 — "add: `class:dragging={draggedIndex === index}`"
- [ ] `<span class="drag-handle" aria-label="Drag to reorder">⋮⋮</span>` present inside `.drag-handle-wrapper` as first child of `<div class="work-header">` in `src/components/ResumeView.svelte`  → source: IMPL_PLAN File 3 — "insert `<span class="drag-handle" aria-label="Drag to reorder">⋮⋮</span>` as the first child"

---

## Section 3 — UX

- [ ] Loading state: existing `resumeData` null check leaves the work list empty during fetch; no change needed — verify the null guard remains intact in `src/components/ResumeView.svelte`  → source: UX_DESIGN "Empty / loading / error states" — "existing `resumeData` null check already handles this. No change."
- [ ] Empty state: empty `<div class="work-list">` renders zero drag handles when `work_experiences` array is empty in `src/components/ResumeView.svelte`  → source: UX_DESIGN "Empty / loading / error states" — "existing layout (an empty `<div class="work-list">`) is unchanged. No drag handles render."
- [ ] Mid-drag state: dragged item has `opacity: 0.5; background: #f0f0f0` via `.work-item.dragging` CSS rule in `src/components/ResumeView.svelte`  → source: UX_DESIGN "State: mid-drag" — "dragged item gets `opacity: 0.5; background: #f0f0f0`"
- [ ] Drop/persist state: on successful drop, existing `saving` state and saved indicator confirms the write in `src/components/ResumeView.svelte`  → source: UX_DESIGN "State: drop / persisting" — "existing `saving` state and `Saved` indicator pattern from `ResumeView.svelte` is reused"
- [ ] Error state on drop failure: existing error Toast shown and `resumeData` reverted from `resume.resume` prop in `src/components/ResumeView.svelte`  → source: UX_DESIGN "State: drop fails" — "fall back to reload…show the existing error pattern. We rely on the existing `Toast` already wired into `ResumeView.svelte`" and IMPL_PLAN File 3 — revert via `resumeData = JSON.parse(JSON.stringify(resume.resume))`

---

## Section 4 — Tests

- [ ] Unit test `test_generate_sorts_work_experiences_chronological` at `tests/test_chronological_order.py` — mocked LLM returns A (2020-01), B (2024-06), C (2022-03); asserts response order is B, C, A  → source: IMPL_PLAN "Test plan" row 1; FEATURE_SPEC Scenario 1
- [ ] Unit test `test_generate_handles_ongoing_jobs_by_start_date` at `tests/test_chronological_order.py` — P (start_date=2024-01, end_date=None) and Q (start_date=2023-06, end_date=2024-12); asserts P before Q  → source: IMPL_PLAN "Test plan" row 2; FEATURE_SPEC Scenario 4
- [ ] Unit test `test_generate_handles_two_ongoing_jobs` at `tests/test_chronological_order.py` — R (start_date=2024-03, end_date=None) and S (start_date=2024-08, end_date=None); asserts S before R  → source: IMPL_PLAN "Test plan" row 3; IMPL_PLAN File 4 "Test 3"
- [ ] Unit test `test_llm_prompts_no_relevance_reorder` at `tests/test_chronological_order.py` — imports `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE`; asserts neither contains the substring `"Reorder work experiences by relevance"`  → source: IMPL_PLAN "Test plan" row 4; FEATURE_SPEC success criteria — "An automated test asserts that the LLM prompts…no longer contain the substring 'Reorder work experiences by relevance'"

---

## Section 5 — Accessibility

- [ ] `aria-label="Drag to reorder"` present on `<span class="drag-handle">` in `src/components/ResumeView.svelte`  → source: UX_DESIGN "Accessibility notes" — "The drag handle uses `aria-label="Drag to reorder"` (same as Languages.svelte line 246)"
- [ ] Drag handle is a `<span>` (not focusable), matching Languages.svelte; no new tab stop introduced — verify no `tabindex` added to the handle  → source: UX_DESIGN "Keyboard nav map" — "`Tab` reaches the drag handle (it's a `<span>`, so technically not focusable; matches Languages.svelte). Recommend NOT changing this in scope"
- [ ] `Tab` still reaches the `Edit` button on each work item — verify existing focus flow is unbroken after drag-handle-wrapper insertion in `src/components/ResumeView.svelte`  → source: UX_DESIGN "Keyboard nav map" — "`Tab` reaches the `Edit` button on each item (already true)"
- [ ] No new tab stops introduced by the drag-drop implementation in `src/components/ResumeView.svelte`  → source: UX_DESIGN "Keyboard nav map" — "The new drag-drop adds no new tab stops"

---

## Section 6 — Project-specific

n/a — no project-checks.md found
