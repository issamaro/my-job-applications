# Checklist: My Job Applications (Unified View)

**Date:** 2026-01-03
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

From LIBRARY_NOTES Section 0:

| Requirement | Version | Verify Command | Status |
|-------------|---------|----------------|--------|
| Node.js | 20.x | `node --version` | [ ] |
| Python | 3.13+ | `python --version` | [ ] |
| nvm | any | `nvm --version` | [ ] |
| uv | any | `uv --version` | [ ] |

- [ ] Node version matches (`nvm use 20`)
- [ ] Virtual environment created (`uv venv --python 3.13`)
- [ ] Virtual environment activated (`source .venv/bin/activate`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

From LIBRARY_NOTES - exact version constraints:

| Library | Constraint | Manifest | Status |
|---------|-----------|----------|--------|
| fastapi | `>=0.100.0` | requirements.txt | [ ] |
| pydantic | `>=2.0` | requirements.txt | [ ] |
| svelte | `^5.0.0` | package.json | [ ] |

**No new dependencies required for this feature.**

**STOP if any dependency has wrong version constraint.**

---

## 2. Syntax Points

From LIBRARY_NOTES - use correct patterns:

### Pydantic v2
- [ ] Optional fields use `field: int | None = None` syntax (not `Optional[int]`)
- [ ] No use of deprecated `.dict()` - use `.model_dump()` instead
- [ ] No use of deprecated `.from_orm()` - use `.model_validate()` instead

### Svelte 5
- [ ] State uses `$state()` rune (not plain `let`)
- [ ] Props use `$props()` rune (not `export let`)
- [ ] Effects use `$effect()` rune (not `$:` reactive statements)
- [ ] Event handlers use `onclick={}` (not `on:click={}`)
- [ ] Derived values use `$derived()` rune (not `$: derived = ...`)

### FastAPI
- [ ] Optional body fields have `= None` default
- [ ] Type hints use `int | None` (not `Union[int, None]`)

---

## 3. UX Points

From UX_DESIGN - implement exactly:

### Section Header
- [ ] Header text: "My Job Applications" (not "Saved Job Descriptions")

### Section States
- [ ] Empty state text: "No job applications yet. Paste a job description above to get started."
- [ ] Loading state: 3 skeleton loaders
- [ ] Error state: "Could not load job applications. Please refresh the page."

### Job Item States
- [ ] Collapsed with resumes: `[v]` toggle visible
- [ ] Collapsed without resumes: No toggle, "0 resumes" as plain text
- [ ] Expanding: Spinner in toggle area
- [ ] Expanded: `[^]` toggle, resume list below
- [ ] Selected: Blue left border highlight

### Auto-expand Rule
- [ ] First (most recent) job expanded by default on page load
- [ ] Other jobs collapsed by default
- [ ] Multiple jobs CAN be expanded simultaneously

### Resume Item Display
- [ ] Format: "Resume · [date] · Match: [score]%" with Delete link
- [ ] Click entire row to load resume in preview panel

### Confirmation Dialogs
- [ ] Delete Job: "Delete Job Application?" with "This will delete the job description and X generated resumes. This cannot be undone."
- [ ] Delete Resume: "Delete Resume?" with "This generated resume will be permanently deleted. This cannot be undone."

### Error Messages
- [ ] Fetch resumes failed: "Could not load resumes"
- [ ] Delete resume failed: "Could not delete resume. Please try again."

---

## 4. Test Points

From FEATURE_SPEC scenarios:

### Backend Unit Tests
- [ ] Test `generate()` with `job_description_id=None` creates new JD
- [ ] Test `generate()` with valid `job_description_id` links to existing JD
- [ ] Test `generate()` updates title from "Untitled Job" to extracted title
- [ ] Test `generate()` preserves custom title (not "Untitled Job")
- [ ] Test `generate()` with non-existent `job_description_id` returns 404

### Frontend Integration Points
- [ ] SavedJobsList passes `onSelectResume` to SavedJobItem
- [ ] SavedJobItem fetches resumes via `getJobDescriptionResumes(id)` on expand
- [ ] SavedJobItem caches fetched resumes (doesn't re-fetch on collapse/expand)
- [ ] ResumeGenerator handles `onSelectResume` to load resume in preview
- [ ] ResumeGenerator passes `loadedJobId` to `generateResume()` call

### BDD Scenario Coverage
- [ ] View my job applications - one section, most recent expanded
- [ ] No separate History section - ResumeHistory component removed
- [ ] Empty state - correct message shown
- [ ] Most recent job auto-expanded
- [ ] Expand a collapsed job - fetches and shows resumes
- [ ] Collapse an expanded job - hides resume list
- [ ] Job with no resumes has no toggle
- [ ] Click resume to view - loads in preview panel
- [ ] Delete resume from expanded list - confirm dialog, update count
- [ ] Generate from loaded job links correctly
- [ ] Generate preserves custom title
- [ ] Generate with no loaded job creates new

---

## 5. Accessibility Points

From UX_DESIGN - implement exactly:

### ARIA Attributes
- [ ] Section collapse button: `aria-expanded="true/false"`
- [ ] Job expand toggle: `aria-expanded="true/false"`
- [ ] Job expand toggle: `aria-controls="resume-list-{job.id}"`
- [ ] Resume list: `role="list"`
- [ ] Resume item: `role="listitem"`
- [ ] Delete buttons: `aria-label="Delete resume for [job title]"`
- [ ] Loading state: `aria-busy="true"`

### Keyboard Navigation
- [ ] Tab navigates between jobs, resumes, buttons
- [ ] Enter/Space toggles expand/collapse
- [ ] Enter/Space activates buttons and selects resume
- [ ] Escape closes confirmation dialog

### Focus Management
- [ ] When job expands: focus moves to first resume item
- [ ] When dialog opens: focus moves to Cancel button
- [ ] When dialog closes: focus returns to triggering button
- [ ] When resume deleted: focus moves to next resume or job toggle

### General
- [ ] All interactive elements keyboard accessible
- [ ] Focus states visible (existing styles)
- [ ] Color contrast meets WCAG 2.1 AA

---

## 6. File Deletion Verification

- [ ] `src/components/ResumeHistory.svelte` - FILE DELETED
- [ ] `src/styles/views/_history.scss` - FILE DELETED
- [ ] `src/styles/views/_index.scss` - `@use "history"` import REMOVED
- [ ] `src/components/ResumeGenerator.svelte` - `import ResumeHistory` REMOVED
- [ ] `src/components/ResumeGenerator.svelte` - `<ResumeHistory>` usage REMOVED
- [ ] `src/components/ResumeGenerator.svelte` - `historyRef` state REMOVED

---

## 7. Implementation Order Verification

### Phase 1: Backend
- [ ] Step 1: `schemas.py` - `job_description_id` field added
- [ ] Step 2-4: `services/resume_generator.py` - linkage logic added
- [ ] Step 5: `routes/resumes.py` - passes `job_description_id`

### Phase 2: Frontend - Expandable Resumes
- [ ] Step 6: `api.js` - `generateResume()` updated
- [ ] Step 7-12: `SavedJobItem.svelte` - expand/collapse functionality

### Phase 3: Frontend - Wire Up
- [ ] Step 13-15: `SavedJobsList.svelte` - header renamed, props added
- [ ] Step 16-18: `ResumeGenerator.svelte` - wired up

### Phase 4: Delete Legacy
- [ ] Steps 19-25: All legacy code removed

### Phase 5: Styles
- [ ] Steps 26-28: New styles added

### Phase 6: Tests
- [ ] Steps 29-31: Tests added

---

## Verification at Closure

Each item above will be checked with `file:line` reference at `/v3-close`.

**Acceptance Criteria Summary:**
1. Generate from existing JD links to same JD (not creates new)
2. All resumes accessible via "My Job Applications" expand
3. No separate "History" section exists
4. First job auto-expands on page load
5. All accessibility requirements met

---

*Contract for /v3-implement*
