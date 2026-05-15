---
feature: chronological-experience-order
date: 2026-05-02
status: VERIFIED
reviewer: analysis-reviewer
---

# Analysis Verified — chronological-experience-order

## Codebase cross-checks (read-only)

- `services/llm/base.py:49` and `:124` — both contain "Reorder work experiences by relevance (most relevant first)". Matches scope IN #1.
- `services/resume_generator.py:185-186` — `ResumeWorkExperience(**we) for we in resume_content.get("work_experiences", [])` — natural insertion point for sort.
- `schemas.py:228-237` — `ResumeWorkExperience` has `start_date: str`, `end_date: str | None`, `included: bool = True`, `order: int = 0`. `WorkExperienceCreate` validator at `schemas.py:58-65` enforces `^\d{4}-(0[1-9]|1[0-2])$` (YYYY-MM), so lexicographic descending sort = chronological descending.
- `src/components/ResumeView.svelte:259-305` — `<ResumeSection title={labels.workExperience}>` block exists exactly at cited lines.
- `src/components/Languages.svelte` — verified anchors L132 `handleDragOver`, L144 `handleDrop`, L156-158 `loadData()` fallback, L246 `<span class="drag-handle" aria-label="Drag to reorder">`, L315-341 CSS block. All UX references byte-accurate.
- `src/components/PdfPreview.svelte:54` — `included !== false` filter applied here (relevant to Scenario 3 — see below).
- `backlog/raw/pattern-drag-drop-reorder.md` — exists.

No hallucinated paths, line numbers, or symbols.

## BDD review

| scenario | testable | finding |
|---|---|---|
| 1 — generation produces chronological (A 2020-01, B 2024-06, C 2022-03 → B,C,A) | Yes | Concrete Given, single When, observable Then on `resume.work_experiences[*]` ordering. Lexicographic sort on YYYY-MM yields asserted order. |
| 2 — drag-drop reorder persists ([A,B,C] → drag B above A → reload → [B,A,C]) | Yes | Concrete stored state, observable post-reload assertion. |
| 3 — included=false hidden, remainder chronological | Yes — surface implicit | Filter `included !== false` lives in `PdfPreview.svelte:54`, NOT the editor list. Then is observable in PDF/preview, not editor. Captured as "almost flagged". |
| 4 — current position (P 2024-01 ongoing, Q 2023-06 ended 2024-12) → P above Q | Yes | Sort is on `start_date` only; `end_date` does not factor in. Implementer must NOT introduce ongoing-first tiebreak. |

All four scenarios pass the testability bar.

## Vague-term findings

Scanned for: appropriate, robust, fast enough, as needed, good UX, intuitive, etc., and so on, reasonable, properly, work correctly, seamless.

| location | term | severity | note |
|---|---|---|---|
| — | — | — | No hits. Scope is enumerated; success criteria concrete; non-functional notes measurable (O(n log n), <20 items). |

## UX state coverage

Surface 1 — Resume Editor (Work Experience drag-drop):

| screen | empty | loading | success | error | status |
|---|---|---|---|---|---|
| Work Experience list | Yes (no handles render on empty array) | Yes (parent `resumeData` null check) | Yes (reuses existing `saving` flag + `Saved` indicator at ResumeView L296-298) | Yes (reload-fallback + existing Toast, mirrors Languages.svelte L156-158) | OK |
| Mid-drag | n/a | n/a | n/a | n/a | covered (`opacity: 0.5; background: #f0f0f0`) |
| Edit-mode on item | n/a | n/a | n/a | n/a | covered (`draggable="true"` only when not editing) |
| Single work item | n/a | n/a | n/a | n/a | covered (handle renders, drop-on-self no-op) |

Surface 2 — Generation flow: no UI footprint, no new states required. OK.

## Traceability

| must_have | covered_by_scenario | status |
|---|---|---|
| 1. Remove "Reorder work experiences by relevance" from `services/llm/base.py` (both occurrences) | Implicit via Scenario 1 + explicit Success-criterion | Covered |
| 2. Sort `work_experiences` by `start_date` desc server-side in `services/resume_generator.py` | Scenarios 1, 4, partially 3 | Covered |
| 3. Drag-drop reorder UI on Work Experience section, persisting via `updateResume` | Scenario 2 | Covered |
| 4. Reorder persists across reloads | Scenario 2 explicitly reloads | Covered |

## Almost flagged but didn't (carry into plan phase)

1. **Scenario 4 sort-key ambiguity for ongoing jobs** — Spec says "sort by `start_date` descending" unambiguously. Add a 2-ongoing-jobs test case to lock the contract (otherwise an implementer could add an `end_date is None ? today : end_date` tiebreaker and still pass).
2. **Scenario 3 visibility surface is implicit** — `included !== false` filtering exists today only in `PdfPreview.svelte:54`. Test against `PdfPreview` / PDF JSON output, not the editor list.
3. **Lexicographic sort is implicit on YYYY-MM strings** — Correct today (`schemas.py:58-65` enforces format on input), but a future schema relaxation would silently break. A single-line note in the implementation about the assumption is warranted.

## Verdict

**VERIFIED** — no BLOCKER, no MAJOR. 4/4 BDD testable, 4/4 must-haves traced, no vague terms, UX states addressed.
