---
feature: chronological-experience-order
date: 2026-05-02
commit_base: HEAD
total_files: 4
total_additions: 176
total_deletions: 2
---

# CHANGE_LOG — Chronological Experience Order

## Backend

| file | change_type | +lines | -lines |
|------|-------------|--------|--------|
| services/llm/base.py | M | 0 | 2 |
| services/resume_generator.py | M | 7 | 0 |

## Frontend

| file | change_type | +lines | -lines |
|------|-------------|--------|--------|
| src/components/ResumeView.svelte | M | 65 | 0 |

## Tests

| file | change_type | +lines | -lines |
|------|-------------|--------|--------|
| tests/test_chronological_order.py | A | 106 | 0 |

## Scope Drift

None. All four changed/added files match the IMPL_PLAN:
- `services/llm/base.py` — removed prompt lines (as planned)
- `services/resume_generator.py` — added `read_experiences_chronologically` helper and call site (as planned)
- `src/components/ResumeView.svelte` — added drag-drop handlers and CSS (as planned)
- `tests/test_chronological_order.py` — new test file with 4 test cases (as planned)

No unplanned files. No omitted planned files.

## Sensitive-Area Changes

None. Changes are isolated to:
- LLM prompt strings (removed a bullet)
- Resume generation logic (new helper function)
- Frontend drag-drop UI (no security impact)
- Test coverage (no sensitive areas)

## Suggested Commit Subject

feat: add drag-drop reorder for work experiences with server-side chronological sort
