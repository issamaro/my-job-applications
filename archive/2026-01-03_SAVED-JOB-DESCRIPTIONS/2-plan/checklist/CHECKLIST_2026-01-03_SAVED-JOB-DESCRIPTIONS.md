# Implementation Checklist: Saved Job Descriptions

**Date:** 2026-01-03
**Status:** Ready for Implementation

---

## Phase 0: Dependencies

### 0.1 Verify Existing Dependencies
- [ ] Verify `fastapi>=0.100.0` in requirements.txt
- [ ] Verify `pydantic>=2.0` in requirements.txt
- [ ] Verify `svelte: ^5.0.0` in package.json
- [ ] No new dependencies required for this feature

**Reference:** LIBRARY_NOTES Section 0 (Dependencies Summary)

---

## Phase 1: Backend (MVP)

### 1.1 Database Migration
- [ ] `database.py`: Add `PRAGMA foreign_keys = ON` to get_db() context manager (enables FK enforcement)
- [ ] `database.py`: Add job_descriptions table columns (title, company_name, updated_at, is_saved)
- [ ] `database.py`: Add job_description_versions table with ON DELETE CASCADE FK
- [ ] `database.py`: Add jd_version_id column to generated_resumes
- [ ] `database.py`: Use try/except for idempotent ALTER TABLE
- [ ] Verify: Run `PRAGMA foreign_keys;` returns 1
- [ ] Verify: Run app, check tables exist with new columns

### 1.2 Schemas
- [ ] `schemas.py`: Add JobDescriptionCreate model (raw_text, min_length=100)
- [ ] `schemas.py`: Add JobDescriptionUpdate model (title, raw_text optional)
- [ ] `schemas.py`: Add JobDescriptionListItem model (id, title, company_name, raw_text_preview, resume_count, created_at, updated_at)
- [ ] `schemas.py`: Add JobDescriptionResponse model (full raw_text)
- [ ] `schemas.py`: Add JobDescriptionWithResumes model (extends Response with resumes list)
- [ ] `schemas.py`: Add JobDescriptionVersion model (Should Have)
- [ ] Verify: Import schemas without error

### 1.3 Service
- [ ] `services/job_descriptions.py`: Create file with JobDescriptionService class
- [ ] `services/job_descriptions.py`: Implement list_all() - ordered by updated_at DESC
- [ ] `services/job_descriptions.py`: Implement get(jd_id) - single JD
- [ ] `services/job_descriptions.py`: Implement create(raw_text) - returns new JD
- [ ] `services/job_descriptions.py`: Implement update(jd_id, data) - title/text update
- [ ] `services/job_descriptions.py`: Implement delete(jd_id) - manual delete resumes (legacy FK), versions auto-cascade
- [ ] `services/job_descriptions.py`: Implement get_resumes(jd_id) - linked resumes
- [ ] `services/job_descriptions.py`: Create singleton instance
- [ ] Verify: Service methods work with database

### 1.4 Router
- [ ] `routes/job_descriptions.py`: Create file with router
- [ ] `routes/job_descriptions.py`: GET / - list all JDs
- [ ] `routes/job_descriptions.py`: POST / - create JD (201 status)
- [ ] `routes/job_descriptions.py`: GET /{jd_id} - get single JD
- [ ] `routes/job_descriptions.py`: PUT /{jd_id} - update JD
- [ ] `routes/job_descriptions.py`: DELETE /{jd_id} - delete JD (204 status)
- [ ] `routes/job_descriptions.py`: GET /{jd_id}/resumes - get linked resumes
- [ ] `main.py`: Import and include job_descriptions router
- [ ] Verify: API endpoints respond correctly

### 1.5 Resume Generator Modification
- [ ] `services/resume_generator.py`: Update generate() to set title from LLM (job_title at company_name)
- [ ] `services/resume_generator.py`: Update generate() to set company_name column
- [ ] `services/resume_generator.py`: Modify delete_resume() to only delete resume, not JD
- [ ] Verify: New resumes have proper JD titles

---

## Phase 2: Frontend (MVP)

### 2.1 API Client
- [ ] `src/lib/api.js`: Add getJobDescriptions()
- [ ] `src/lib/api.js`: Add createJobDescription(rawText)
- [ ] `src/lib/api.js`: Add getJobDescription(id)
- [ ] `src/lib/api.js`: Add updateJobDescription(id, data)
- [ ] `src/lib/api.js`: Add deleteJobDescription(id)
- [ ] `src/lib/api.js`: Add getJobDescriptionResumes(id)
- [ ] Verify: API calls work from browser console

### 2.2 Styles
- [ ] `src/styles/views/_saved-jobs.scss`: Create file
- [ ] `src/styles/views/_saved-jobs.scss`: Add .saved-jobs-section styles
- [ ] `src/styles/views/_saved-jobs.scss`: Add .saved-jobs-header styles (collapsible)
- [ ] `src/styles/views/_saved-jobs.scss`: Add .saved-jobs-content styles
- [ ] `src/styles/views/_saved-jobs.scss`: Add .saved-job-item styles
- [ ] `src/styles/views/_saved-jobs.scss`: Add .selected state (blue left border)
- [ ] `src/styles/views/_saved-jobs.scss`: Add .job-info, .job-title, .job-preview styles
- [ ] `src/styles/views/_saved-jobs.scss`: Add .title-input styles (inline editing)
- [ ] `src/styles/views/_saved-jobs.scss`: Add .empty-state styles
- [ ] `src/styles/views/_index.scss`: Add @forward "saved-jobs"
- [ ] `src/styles/views/_resume-generator.scss`: Add .loaded-indicator styles
- [ ] `src/styles/views/_resume-generator.scss`: Add .button-row styles
- [ ] Verify: CSS compiles without errors

### 2.3 SavedJobItem Component
- [ ] `src/components/SavedJobItem.svelte`: Create file
- [ ] `src/components/SavedJobItem.svelte`: Accept job, selected, onLoad, onDelete props
- [ ] `src/components/SavedJobItem.svelte`: Display title, preview (200 chars), meta (date, resume count)
- [ ] `src/components/SavedJobItem.svelte`: Inline title editing (pencil icon, input, Enter/Escape)
- [ ] `src/components/SavedJobItem.svelte`: Delete button with stopPropagation
- [ ] `src/components/SavedJobItem.svelte`: Selected state visual (blue border)
- [ ] `src/components/SavedJobItem.svelte`: ARIA labels for accessibility
- [ ] Verify: Component renders correctly in isolation

### 2.4 SavedJobsList Component
- [ ] `src/components/SavedJobsList.svelte`: Create file
- [ ] `src/components/SavedJobsList.svelte`: Accept onLoad, selectedId props
- [ ] `src/components/SavedJobsList.svelte`: Load jobs on mount with $effect
- [ ] `src/components/SavedJobsList.svelte`: Collapsible header (like ResumeHistory)
- [ ] `src/components/SavedJobsList.svelte`: Loading state (3 skeletons)
- [ ] `src/components/SavedJobsList.svelte`: Empty state with hint message
- [ ] `src/components/SavedJobsList.svelte`: Render SavedJobItem for each job
- [ ] `src/components/SavedJobsList.svelte`: Delete confirmation dialog with resume count warning
- [ ] `src/components/SavedJobsList.svelte`: Export refresh() method
- [ ] Verify: Component loads and displays jobs

### 2.5 JobDescriptionInput Modifications
- [ ] `src/components/JobDescriptionInput.svelte`: Add saving, loadedJobId, loadedJobTitle props
- [ ] `src/components/JobDescriptionInput.svelte`: Add onSave, onClear callbacks
- [ ] `src/components/JobDescriptionInput.svelte`: Display loaded indicator when job loaded
- [ ] `src/components/JobDescriptionInput.svelte`: Clear button in loaded indicator
- [ ] `src/components/JobDescriptionInput.svelte`: Save button disabled when invalid or saving
- [ ] `src/components/JobDescriptionInput.svelte`: "Saving..." text during save
- [ ] Verify: Save button works, indicator shows when loaded

### 2.6 ResumeGenerator Integration
- [ ] `src/components/ResumeGenerator.svelte`: Import SavedJobsList
- [ ] `src/components/ResumeGenerator.svelte`: Add loadedJobId, loadedJobTitle state
- [ ] `src/components/ResumeGenerator.svelte`: Add saving state
- [ ] `src/components/ResumeGenerator.svelte`: Add savedJobsRef for refresh
- [ ] `src/components/ResumeGenerator.svelte`: Implement handleLoadJob(id, rawText)
- [ ] `src/components/ResumeGenerator.svelte`: Implement handleClearLoaded()
- [ ] `src/components/ResumeGenerator.svelte`: Implement handleSaveJob() with create/update logic
- [ ] `src/components/ResumeGenerator.svelte`: Pass new props to JobDescriptionInput
- [ ] `src/components/ResumeGenerator.svelte`: Add SavedJobsList between JD input and History
- [ ] `src/components/ResumeGenerator.svelte`: Refresh savedJobsRef after generate
- [ ] Verify: Full flow works end-to-end

---

## Phase 3: Should Have (Version History)

### 3.1 Backend Version History
- [ ] `services/job_descriptions.py`: Implement get_versions(jd_id)
- [ ] `services/job_descriptions.py`: Implement restore_version(jd_id, version_id)
- [ ] `services/job_descriptions.py`: Update update() to create version when text changes
- [ ] `routes/job_descriptions.py`: GET /{jd_id}/versions endpoint
- [ ] `routes/job_descriptions.py`: POST /{jd_id}/versions/{version_id}/restore endpoint
- [ ] Verify: Version history API works

### 3.2 Frontend Version History (Optional)
- [ ] `src/lib/api.js`: Add getJobDescriptionVersions(id)
- [ ] `src/lib/api.js`: Add restoreJobDescriptionVersion(jdId, versionId)
- [ ] UI for version history (if time permits)

---

## Testing Checklist

### Backend API Tests
- [ ] POST /api/job-descriptions - valid text returns 201
- [ ] POST /api/job-descriptions - short text returns 400
- [ ] GET /api/job-descriptions - returns list ordered by updated_at
- [ ] GET /api/job-descriptions/{id} - returns single JD with resume_count
- [ ] GET /api/job-descriptions/{id} - non-existent returns 404
- [ ] PUT /api/job-descriptions/{id} - update title works
- [ ] PUT /api/job-descriptions/{id} - update text works
- [ ] DELETE /api/job-descriptions/{id} - returns 204
- [ ] DELETE /api/job-descriptions/{id} - cascades to resumes (verify no orphaned rows)
- [ ] DELETE /api/job-descriptions/{id} - cascades to versions (FK CASCADE auto)
- [ ] GET /api/job-descriptions/{id}/resumes - returns linked resumes
- [ ] Verify PRAGMA foreign_keys = ON on test connection

### Frontend Manual Tests
- [ ] Save button disabled when < 100 chars
- [ ] Save button enabled when >= 100 chars
- [ ] Save creates new JD, appears in list
- [ ] Click JD loads into textarea
- [ ] Loaded indicator shows when JD loaded
- [ ] Clear button removes loaded state
- [ ] Edit title with pencil icon works
- [ ] Enter saves title, Escape cancels
- [ ] Delete shows confirmation with resume count
- [ ] Delete removes JD from list
- [ ] Generate updates resume count in list
- [ ] Panel collapses/expands
- [ ] Empty state shows when no JDs

### Accessibility Tests
- [ ] Tab navigation works through all elements
- [ ] Focus states visible
- [ ] Screen reader announces states correctly
- [ ] Delete confirmation is modal
- [ ] ARIA labels present

---

## Definition of Done

### MVP Complete When:
1. All Phase 1 items checked
2. All Phase 2 items checked
3. All Backend API Tests pass
4. All Frontend Manual Tests pass
5. All Accessibility Tests pass

### Feature Complete When:
1. MVP Complete
2. All Phase 3 items checked (if time permits)

---

*Checklist Complete | Ready for /v3-verify-plan*
