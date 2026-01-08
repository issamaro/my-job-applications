# Retrospective: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| What went well | Planning was thorough, Implementation was smooth, Quick iteration | Documented in What Worked Well |
| What could improve | Photo handling gap, More integration testing | Documented in What Could Improve |
| Patterns to document | A) Yes - data flow patterns | Created backlog item |

---

## 1. What Worked Well

### Planning
- **IMPL_PLAN was comprehensive:** Clear step-by-step implementation order helped execute efficiently
- **CHECKLIST caught details:** CSS patterns, accessibility checks were pre-planned
- **LIBRARY_NOTES research:** WeasyPrint CSS Grid guidance avoided trial-and-error

### Implementation
- **Followed existing patterns:** New templates mirrored existing structure
- **Clear file boundaries:** Backend/frontend separation made changes isolated
- **Test-first for new tests:** Adding tests alongside implementation caught regressions

### Iteration
- **Quick feedback loop:** Manual inspection caught the photo issue fast
- **Hot fix during inspection:** Fixed and re-verified in same session
- **Tests confirmed fix:** 51 tests passed after the photo fix

---

## 2. What Could Improve

### Blockers
- **Photo data flow not analyzed:** FEATURE_SPEC noted photo was "excluded from LLM calls" but didn't trace the full data path to resume storage/retrieval
- **Gap between "confirmed" and "tested":** Assumption said "photo available" but actual integration wasn't verified until inspection

### Rework
- **Photo fix required during inspection:** Had to modify `resume_generator.py` twice (save/restore photo, then fetch from profile for existing resumes)
- **Fix was straightforward but should have been in IMPL_PLAN**

### Gaps
- **No integration test for photo in PDF:** Unit tests mocked PDF generation, didn't verify actual photo embedding
- **E2E test would have caught this:** A test that generates a resume then checks photo presence

---

## 3. Assumption Review

| Assumption | Correct? | When Discovered | Impact |
|------------|----------|-----------------|--------|
| Photo in `personal_info.photo` as base64 | YES | Planning | Correctly identified location |
| Photo excluded from LLM calls but available in DB | PARTIALLY | Inspection | Available in DB but NOT restored to resume_content |
| WeasyPrint renders base64 images | YES | Testing | Worked as expected |
| Two-column CSS works in WeasyPrint | YES | Testing | CSS Grid worked perfectly |
| Existing tests don't rely on template count | YES | Testing | No hardcoded assertions found |

**Key Learning:** "Photo excluded from LLM calls" was correct, but the assumption didn't account for the need to RESTORE the photo after the LLM call. The data flow was:
```
profile → [remove photo] → LLM → resume_content → [photo missing!]
```
Should have been:
```
profile → [remove photo, save aside] → LLM → [restore photo] → resume_content
```

---

## 4. Actionable Findings

| Finding | Backlog Item? | File Created |
|---------|---------------|--------------|
| Document data flow patterns for complex fields | YES | `backlog/raw/data-flow-documentation.md` |
| Add integration test for photo in PDF | NO | Small enough to include in next feature |

---

## 5. Process Feedback

| Phase | Worked? | Notes |
|-------|---------|-------|
| /v5-scope | YES | Clear requirements from refined backlog |
| /v5-analyze | YES | Thorough spec, good assumption documentation |
| /v5-plan | MOSTLY | Missed photo data flow edge case |
| /v5-build | YES | Implementation + tests + inspection worked well |
| /v5-ship | YES | Clean closure process |

---

## Summary

**Top Lesson:** When an assumption says "data is available," trace the FULL data path from source to destination. Especially for fields that are modified mid-pipeline (like photo being stripped for LLM calls).

**Positive Pattern:** Quick iteration during inspection - found issue, fixed, re-verified in same session. The v5-inspect step proved valuable.

---

*Retrospective completed: 2026-01-08*
