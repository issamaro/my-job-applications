# Retrospective: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language

## What Worked Well

### Planning
- **Clear requirements** - UX design and checklist made implementation straightforward
- Feature spec with BDD scenarios provided clear acceptance criteria
- CEFR level decision (codes only) clarified early, avoided rework

### Implementation
- **Smooth implementation** - Code followed existing patterns (Education.svelte) well
- Minimal surprises during coding
- Existing component patterns (Section, ConfirmDialog) made UI development fast

### Testing
- **Fast iteration** - Quick feedback loops, minimal rework needed
- All 11 feature-specific tests passed first run
- Test coverage for API and validation was comprehensive

### Tooling
- uv/pytest workflow worked smoothly
- Svelte 5 patterns well-established in codebase

## What Could Improve

**Nothing notable** - Process worked well for this feature.

### Minor Observations
- pytest-cov not in dev dependencies (coverage step skipped)
- One unrelated test failure (test_data_url_too_large in photos) - pre-existing issue

## Assumption Review

| Assumption | Correct? | When Discovered | Impact |
|------------|----------|-----------------|--------|
| Languages display in user-defined order via drag-and-drop | Yes | Build phase | Worked as designed |
| Only CEFR level codes shown in output (not descriptions) | Yes | Implementation | Clean resume output |
| Follow existing section patterns (Skills, Education) | Yes | Implementation | Fast development |
| Use same ResumeSection wrapper component | Yes | Implementation | UI consistency achieved |
| Single database table with foreign key to user | Yes | Implementation | Standard pattern worked |

**All assumptions validated** - no surprises during implementation.

## Actionable Findings

### Pattern Documentation Opportunities

Two patterns identified worth documenting for future features:

| Finding | Backlog Item Created |
|---------|---------------------|
| CEFR level pattern (Enum with descriptions) | `backlog/raw/pattern-enum-with-descriptions.md` |
| Drag-and-drop reordering pattern | `backlog/raw/pattern-drag-drop-reorder.md` |

## Process Feedback

| Phase | Worked? | Notes |
|-------|---------|-------|
| /v5-scope | Yes | Clear refinement from raw idea |
| /v5-analyze | Yes | Requirements + UX captured well |
| /v5-plan | Yes | Checklist comprehensive |
| /v5-build | Yes | Implementation + test + inspect smooth |
| /v5-ship | Yes | Reflection capturing value |

## Summary

**Top Lesson:** Following existing component patterns (Education.svelte) significantly accelerated development. The 73-item checklist from /v5-plan ensured nothing was missed.

**Recommendation:** When adding similar CRUD sections in future, reference Languages/Education as canonical patterns.

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| What went well | Smooth implementation, Clear requirements, Fast iteration | Documented in Worked Well section |
| What could improve | Nothing notable | No blockers or rework identified |
| Patterns to document | CEFR level pattern + Drag-and-drop pattern | Created 2 backlog/raw items |
