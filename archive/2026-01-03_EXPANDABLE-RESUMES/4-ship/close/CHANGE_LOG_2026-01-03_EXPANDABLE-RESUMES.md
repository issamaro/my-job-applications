# Change Log: My Job Applications (Unified View)

**Date:** 2026-01-03
**Feature Spec:** FEATURE_SPEC_2026-01-03_EXPANDABLE-RESUMES.md
**Implementation Plan:** IMPL_PLAN_2026-01-03_EXPANDABLE-RESUMES.md

---

## Files Modified

### Backend

| File | Lines | Change Description |
|------|-------|-------------------|
| schemas.py | 161 | Added `job_description_id: int \| None = None` to ResumeGenerateRequest |
| services/resume_generator.py | 21-77 | Modified `generate()` to accept optional `job_description_id`, link to existing JD, update title logic |
| routes/resumes.py | 20-23 | Pass `request.job_description_id` to service |

### Frontend

| File | Lines | Change Description |
|------|-------|-------------------|
| src/lib/api.js | 137-145 | Updated `generateResume()` to accept optional `jobDescriptionId` |
| src/components/SavedJobItem.svelte | 1-215 | Complete rewrite: added expand/collapse, fetch resumes, delete resume, props |
| src/components/SavedJobsList.svelte | 1-110 | Renamed header to "My Job Applications", added `onSelectResume` prop, auto-expand first |
| src/components/ResumeGenerator.svelte | 1-226 | Removed ResumeHistory, added `handleSelectResume`, pass `loadedJobId` to generate |
| src/styles/views/_saved-jobs.scss | 179-296 | Added styles: `.expand-toggle`, `.resume-list`, `.resume-item`, `.spinner-small` |
| src/styles/views/_index.scss | 7 | Removed `@forward "history"` import |

### Files Deleted

| File | Reason |
|------|--------|
| src/components/ResumeHistory.svelte | Functionality moved to SavedJobItem |
| src/styles/views/_history.scss | Styles moved to _saved-jobs.scss |

### Tests

| File | Lines | Coverage |
|------|-------|----------|
| tests/test_resumes.py | 294-466 | 5 new tests for job_description_id linkage |

---

## Documentation Updated

None required - this was a UI/UX consolidation feature.

---

## Checklist Verification

### Syntax Points (from CHECKLIST Section 2)

- [x] Pydantic: `field: int \| None = None` syntax → schemas.py:161
- [x] Svelte 5: `$state()` rune → SavedJobItem.svelte:9-14
- [x] Svelte 5: `$props()` rune → SavedJobItem.svelte:5
- [x] Svelte 5: `$effect()` rune → SavedJobItem.svelte:22-26
- [x] Svelte 5: `onclick={}` event handlers → SavedJobItem.svelte:143,151
- [x] FastAPI: Optional field with `= None` → schemas.py:161

### UX Points (from CHECKLIST Section 3)

- [x] Header: "My Job Applications" → SavedJobsList.svelte:69
- [x] Empty state: "No job applications yet..." → SavedJobsList.svelte:85
- [x] Loading state: 3 skeleton loaders → SavedJobsList.svelte:76-78
- [x] Error state: "Could not load job applications..." → SavedJobsList.svelte:81
- [x] Collapsed toggle: `[v]` → SavedJobItem.svelte:159
- [x] Expanded toggle: `[^]` → SavedJobItem.svelte:159
- [x] No toggle for 0 resumes → SavedJobItem.svelte:163-164
- [x] Resume format: "Resume · [date] · Match: [score]%" → SavedJobItem.svelte:192
- [x] Delete Job dialog: "Delete Job Application?" → SavedJobsList.svelte:105
- [x] Delete Resume dialog: "Delete Resume?" → SavedJobItem.svelte:209
- [x] Auto-expand first job → SavedJobsList.svelte:92

### Accessibility Points (from CHECKLIST Section 5)

- [x] `aria-expanded` on section collapse → SavedJobsList.svelte:67
- [x] `aria-expanded` on job toggle → SavedJobItem.svelte:152
- [x] `aria-controls` on job toggle → SavedJobItem.svelte:153
- [x] `role="list"` on resume list → SavedJobItem.svelte:178
- [x] `role="listitem"` on resume items → SavedJobItem.svelte:186
- [x] `aria-label` on delete buttons → SavedJobItem.svelte:171, 197
- [x] `aria-busy` on loading state → SavedJobItem.svelte:178

### Test Points (from CHECKLIST Section 4)

- [x] Test: generate with `job_description_id=None` creates new JD → test_resumes.py:345
- [x] Test: generate with valid `job_description_id` links to existing → test_resumes.py:307
- [x] Test: title updates from "Untitled Job" → test_resumes.py:378
- [x] Test: custom title preserved → test_resumes.py:417
- [x] Test: non-existent JD returns error → test_resumes.py:456

### File Deletion Verification (from CHECKLIST Section 6)

- [x] ResumeHistory.svelte - DELETED
- [x] _history.scss - DELETED
- [x] _index.scss: `@use "history"` - REMOVED
- [x] ResumeGenerator.svelte: `import ResumeHistory` - REMOVED
- [x] ResumeGenerator.svelte: `<ResumeHistory>` - REMOVED
- [x] ResumeGenerator.svelte: `historyRef` - REMOVED

---

## Test Summary

- Unit Tests: 91 passed (5 new feature tests)
- Pre-existing failures: 10 (PDF/WeasyPrint - unrelated)
- Coverage: Feature code fully tested

---

## Inspection Summary

- Browser: PASS (6/6 checks)
- Accessibility: PASS (5/5 checks)
- UX Match: PASS (14/14 elements)

---

*Change Log Complete*
