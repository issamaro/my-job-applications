# Implementation Plan: My Job Applications (Unified View)

**Date:** 2026-01-03
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-03_EXPANDABLE-RESUMES.md

---

## 1. Affected Files

### Config/Dependencies

| File | Change | Description |
|------|--------|-------------|
| `requirements.txt` | None | No new dependencies needed |
| `package.json` | None | No new dependencies needed |

### Backend

| File | Change | Description |
|------|--------|-------------|
| `schemas.py` | Modify | Add `job_description_id: int \| None = None` to `ResumeGenerateRequest` |
| `services/resume_generator.py` | Modify | Accept optional `job_description_id`, link to existing JD, update title logic |
| `routes/resumes.py` | Modify | Pass `job_description_id` from request to service |

### Frontend

| File | Change | Description |
|------|--------|-------------|
| `src/components/ResumeGenerator.svelte` | Modify | Remove ResumeHistory import and usage, pass `loadedJobId` to generate |
| `src/components/SavedJobsList.svelte` | Modify | Rename header to "My Job Applications", add `onSelectResume` prop, auto-expand first job |
| `src/components/SavedJobItem.svelte` | Modify | Add expand/collapse toggle, fetch resumes on expand, display resume list, delete resume |
| `src/components/ResumeHistory.svelte` | Delete | Functionality moved to SavedJobItem |
| `src/lib/api.js` | Modify | Update `generateResume()` to accept optional `jobDescriptionId` |
| `src/styles/views/_saved-jobs.scss` | Modify | Add resume list styles (`.resume-list`, `.resume-item`) |
| `src/styles/views/_history.scss` | Delete | Styles moved to _saved-jobs.scss |
| `src/styles/views/_index.scss` | Modify | Remove `_history.scss` import |

### Tests

| File | Change | Description |
|------|--------|-------------|
| `tests/test_resumes.py` | Modify | Add tests for `job_description_id` linkage |

### Documentation

| File | Change | Description |
|------|--------|-------------|
| None | - | No documentation changes needed |

---

## 2. Database Changes

```sql
-- None - existing schema supports all requirements
-- job_descriptions.id already links to generated_resumes.job_description_id
```

---

## 3. Implementation Approach

### 3.1 Backend: JD-Resume Linkage Fix

**Current Behavior:**
`generate()` always creates a NEW `job_descriptions` row, even when user loads an existing JD.

**New Behavior:**
1. Accept optional `job_description_id` in request
2. If provided: link resume to EXISTING JD, update title only if "Untitled Job"
3. If not provided: create NEW JD (preserve current behavior)

```python
# schemas.py
class ResumeGenerateRequest(BaseModel):
    job_description: str
    job_description_id: int | None = None  # NEW: optional link to existing JD

# services/resume_generator.py
async def generate(self, job_description: str, job_description_id: int | None = None):
    ...
    if job_description_id:
        # Link to existing JD
        jd_id = job_description_id
        # Update title only if still "Untitled Job"
        cursor = conn.execute("SELECT title FROM job_descriptions WHERE id = ?", (jd_id,))
        existing = cursor.fetchone()
        if existing and existing["title"] == "Untitled Job":
            new_title = f"{job_title} at {company_name}"
            conn.execute("UPDATE job_descriptions SET title = ?, company_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (new_title, company_name, jd_id))
        else:
            # Just update timestamp
            conn.execute("UPDATE job_descriptions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (jd_id,))
    else:
        # Create new JD (existing behavior)
        cursor = conn.execute(...)
        jd_id = cursor.lastrowid
```

### 3.2 Frontend: Expandable Resumes in SavedJobItem

**Pattern:** On-demand fetch when user expands

```svelte
<!-- SavedJobItem.svelte -->
<script>
  let expanded = $state(false);
  let resumes = $state([]);
  let loadingResumes = $state(false);
  let resumesFetched = $state(false);  // Cache flag
  let deleteResumeId = $state(null);

  async function toggleExpand() {
    if (!expanded && !resumesFetched && job.resume_count > 0) {
      loadingResumes = true;
      try {
        resumes = await getJobDescriptionResumes(job.id);
        resumesFetched = true;
      } catch (e) {
        console.error('Failed to load resumes:', e);
      } finally {
        loadingResumes = false;
      }
    }
    expanded = !expanded;
  }
</script>

{#if job.resume_count > 0}
  <button onclick={toggleExpand} aria-expanded={expanded}>
    {expanded ? '[^]' : '[v]'}
  </button>
{/if}

{#if expanded}
  <div class="resume-list" role="list">
    {#if loadingResumes}
      <div class="skeleton"></div>
    {:else}
      {#each resumes as resume}
        <div class="resume-item" role="listitem">
          <button onclick={() => onSelectResume(resume.id)}>
            Resume · {formatDate(resume.created_at)} · {resume.match_score}%
          </button>
          <button onclick={() => deleteResumeId = resume.id}>Delete</button>
        </div>
      {/each}
    {/if}
  </div>
{/if}
```

### 3.3 Frontend: Remove ResumeHistory Component

**Before:**
```
ResumeGenerator.svelte
  ├── SavedJobsList (shows JDs)
  └── ResumeHistory (shows all resumes - REMOVE)
```

**After:**
```
ResumeGenerator.svelte
  └── SavedJobsList (shows JDs with expandable resumes)
        └── SavedJobItem (expand to see linked resumes)
```

### 3.4 Frontend: Pass loadedJobId to Generate

```javascript
// api.js
export async function generateResume(jobDescription, jobDescriptionId = null) {
  const body = { job_description: jobDescription };
  if (jobDescriptionId) {
    body.job_description_id = jobDescriptionId;
  }
  return request('/resumes/generate', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

// ResumeGenerator.svelte
const result = await generateResume(jobDescription, loadedJobId);
```

### 3.5 Auto-expand First Job

```svelte
<!-- SavedJobsList.svelte -->
let { onLoad, onSelectResume, selectedId = null } = $props();

{#each jobs as job, index}
  <SavedJobItem
    {job}
    selected={selectedId === job.id}
    autoExpand={index === 0}
    {onLoad}
    onDelete={confirmDelete}
    {onSelectResume}
  />
{/each}
```

### 3.6 Error Handling

| Error | Handler | User Feedback |
|-------|---------|---------------|
| Fetch resumes fails | Catch in toggleExpand | "Could not load resumes" inline |
| Delete resume fails | Catch in handleDeleteResume | "Could not delete. Try again." |
| JD not found (linkage) | Backend returns 404 | Falls back to create new JD |

---

## 4. Implementation Order

### Phase 1: Backend (Safe, Additive)

1. [ ] `schemas.py:159-168` - Add `job_description_id: int | None = None` to `ResumeGenerateRequest`
2. [ ] `services/resume_generator.py:21` - Modify `generate()` signature to accept `job_description_id`
3. [ ] `services/resume_generator.py:32-46` - Add conditional logic: if `job_description_id` provided, link to existing JD
4. [ ] `services/resume_generator.py:34-36` - Add title update logic (only if "Untitled Job")
5. [ ] `routes/resumes.py:18-21` - Pass `request.job_description_id` to service

### Phase 2: Frontend - Expandable Resumes

6. [ ] `src/lib/api.js:137-142` - Update `generateResume()` to accept optional `jobDescriptionId`
7. [ ] `src/components/SavedJobItem.svelte` - Add state: `expanded`, `resumes`, `loadingResumes`, `resumesFetched`, `deleteResumeId`
8. [ ] `src/components/SavedJobItem.svelte` - Add `toggleExpand()` function with fetch logic
9. [ ] `src/components/SavedJobItem.svelte` - Add expand/collapse toggle button (only if `resume_count > 0`)
10. [ ] `src/components/SavedJobItem.svelte` - Add resume list rendering with `{#if expanded}`
11. [ ] `src/components/SavedJobItem.svelte` - Add `handleDeleteResume()` with confirm dialog
12. [ ] `src/components/SavedJobItem.svelte` - Add props: `onSelectResume`, `autoExpand`

### Phase 3: Frontend - Wire Up Parent Components

13. [ ] `src/components/SavedJobsList.svelte` - Change header from "Saved Job Descriptions" to "My Job Applications"
14. [ ] `src/components/SavedJobsList.svelte` - Add `onSelectResume` prop and pass to SavedJobItem
15. [ ] `src/components/SavedJobsList.svelte` - Pass `autoExpand={index === 0}` to first item
16. [ ] `src/components/ResumeGenerator.svelte` - Add `handleSelectResume(id)` function
17. [ ] `src/components/ResumeGenerator.svelte` - Pass `onSelectResume={handleSelectResume}` to SavedJobsList
18. [ ] `src/components/ResumeGenerator.svelte:60` - Pass `loadedJobId` to `generateResume()` call

### Phase 4: Delete Legacy

19. [ ] `src/components/ResumeGenerator.svelte:5` - Remove `import ResumeHistory`
20. [ ] `src/components/ResumeGenerator.svelte:203` - Remove `<ResumeHistory>` component usage
21. [ ] `src/components/ResumeGenerator.svelte:15` - Remove `historyRef` state
22. [ ] `src/components/ResumeGenerator.svelte:63` - Remove `historyRef?.refresh()` calls
23. [ ] `src/components/ResumeHistory.svelte` - **DELETE FILE**
24. [ ] `src/styles/views/_history.scss` - **DELETE FILE**
25. [ ] `src/styles/views/_index.scss` - Remove `@use "history"` import

### Phase 5: Styles

26. [ ] `src/styles/views/_saved-jobs.scss` - Add `.expand-toggle` styles
27. [ ] `src/styles/views/_saved-jobs.scss` - Add `.resume-list` styles
28. [ ] `src/styles/views/_saved-jobs.scss` - Add `.resume-item` styles (reuse from _history.scss)

### Phase 6: Tests

29. [ ] `tests/test_resumes.py` - Add test: generate with `job_description_id` links to existing JD
30. [ ] `tests/test_resumes.py` - Add test: title updates only if "Untitled Job"
31. [ ] `tests/test_resumes.py` - Add test: generate without `job_description_id` creates new JD (existing behavior)

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Breaking existing generate flow | Low | High | `job_description_id` is optional, default behavior unchanged |
| Resume fetch on expand causes lag | Med | Low | Add loading spinner, cache after first fetch |
| Deleting wrong resume | Low | Med | Confirm dialog required before delete |
| JD referenced by `job_description_id` doesn't exist | Low | Med | Backend returns 404, frontend falls back to create new |

---

## 6. Validation Checklist (Post-Implementation)

- [ ] Generate from new JD creates new job_descriptions row
- [ ] Generate from loaded JD links to existing job_descriptions row
- [ ] Title updates from "Untitled Job" but preserves custom titles
- [ ] Expand toggle only shows when resume_count > 0
- [ ] First job auto-expands on page load
- [ ] Clicking resume loads it in preview panel
- [ ] Delete resume removes from list and decrements count
- [ ] ResumeHistory component fully removed
- [ ] No regression in existing Save/Edit/Delete JD functionality

---

*Next: /v3-checklist*
