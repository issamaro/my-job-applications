# Implementation Plan: Saved Job Descriptions

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Implementation Overview

### 1.1 Scope Summary
Implement a "Saved Job Descriptions" feature allowing users to:
- Save JDs independently or automatically on generate
- List, load, edit, and delete saved JDs
- Link resumes to their source JD
- (Should Have) Track and restore JD versions

### 1.2 Architecture Impact
- **Database**: 3 ALTER TABLE + 1 new table
- **Backend**: 1 new service + 1 new router + schema updates
- **Frontend**: 2 new components + 2 modified components + 1 new SCSS file
- **Existing Behavior**: Modified resume generation to link JDs

---

## 2. File Changes

### 2.1 Database Migration

| File | Change Type | Description |
|------|-------------|-------------|
| `database.py` | Modify | Add PRAGMA foreign_keys + new table + ALTER TABLE statements |

**Details:**

```python
# 1. Update get_db() to enable FK enforcement on every connection
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK cascade
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# 2. Add to init_db() function - migrations
# Migrations for job_descriptions table
conn.executescript("""
    -- Add new columns if not exist (use try/except for idempotency)
    ALTER TABLE job_descriptions ADD COLUMN title TEXT DEFAULT 'Untitled Job';
    ALTER TABLE job_descriptions ADD COLUMN company_name TEXT;
    ALTER TABLE job_descriptions ADD COLUMN updated_at TEXT;
    ALTER TABLE job_descriptions ADD COLUMN is_saved INTEGER DEFAULT 1;
""")

# Backfill updated_at
conn.execute("""
    UPDATE job_descriptions SET updated_at = created_at WHERE updated_at IS NULL
""")

# New version history table (Should Have)
conn.executescript("""
    CREATE TABLE IF NOT EXISTS job_description_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_description_id INTEGER NOT NULL,
        raw_text TEXT NOT NULL,
        version_number INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
    );

    ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER;
""")
```

**Implementation Notes:**
- SQLite ALTER TABLE will fail if column exists. Wrap in try/except or check sqlite_master first.
- `PRAGMA foreign_keys = ON` must be set on **every connection** (not just in init_db)
- With PRAGMA enabled, ON DELETE CASCADE in FK definitions will auto-delete child rows

---

### 2.2 Backend - Schemas

| File | Change Type | Description |
|------|-------------|-------------|
| `schemas.py` | Modify | Add 6 new Pydantic models for JD CRUD |

**New Models:**

```python
# Job Description schemas
class JobDescriptionCreate(BaseModel):
    raw_text: str = Field(..., min_length=100)

    @field_validator("raw_text")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip()


class JobDescriptionUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    raw_text: str | None = None

    @field_validator("raw_text")
    @classmethod
    def validate_length(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v.strip() if v else v


class JobDescriptionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    raw_text_preview: str  # First 200 chars
    resume_count: int
    created_at: str
    updated_at: str


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str | None = None
    raw_text: str
    resume_count: int
    created_at: str
    updated_at: str


class JobDescriptionWithResumes(JobDescriptionResponse):
    resumes: list[ResumeHistoryItem] = []


# Version History (Should Have)
class JobDescriptionVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_number: int
    raw_text: str
    created_at: str
```

---

### 2.3 Backend - Service

| File | Change Type | Description |
|------|-------------|-------------|
| `services/job_descriptions.py` | Create | New service for JD CRUD operations |

**Class Structure:**

```python
class JobDescriptionService:
    def list_all(self) -> list[dict]:
        """Get all saved JDs with resume count, ordered by updated_at DESC"""

    def get(self, jd_id: int) -> dict | None:
        """Get single JD by ID"""

    def get_with_resumes(self, jd_id: int) -> dict | None:
        """Get JD with linked resumes"""

    def create(self, raw_text: str) -> dict:
        """Save new JD with default title"""

    def update(self, jd_id: int, data: dict) -> dict | None:
        """Update JD title or text, create version if text changed"""

    def delete(self, jd_id: int) -> bool:
        """Delete JD and cascade to resumes + versions"""

    def get_resumes(self, jd_id: int) -> list[dict]:
        """Get resumes linked to this JD"""

    # Should Have
    def get_versions(self, jd_id: int) -> list[dict]:
        """Get version history for JD"""

    def restore_version(self, jd_id: int, version_id: int) -> dict | None:
        """Restore JD text from version (creates new version)"""

job_description_service = JobDescriptionService()
```

**Key Implementation Details:**

1. **Cascade Delete Pattern (simplified with PRAGMA foreign_keys):**
```python
def delete(self, jd_id: int) -> bool:
    with get_db() as conn:
        # PRAGMA foreign_keys = ON is set in get_db()
        # ON DELETE CASCADE handles child records automatically
        cursor = conn.execute(
            "DELETE FROM job_descriptions WHERE id = ?",
            (jd_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
```

**Note:** The existing `generated_resumes` FK lacks ON DELETE CASCADE. We need to either:
- Recreate the table with CASCADE (disruptive), OR
- Keep manual delete for resumes only (hybrid approach)

**Recommended hybrid approach:**
```python
def delete(self, jd_id: int) -> bool:
    with get_db() as conn:
        # Manual delete for legacy FK without CASCADE
        conn.execute(
            "DELETE FROM generated_resumes WHERE job_description_id = ?",
            (jd_id,)
        )
        # job_description_versions has CASCADE, auto-deletes
        cursor = conn.execute(
            "DELETE FROM job_descriptions WHERE id = ?",
            (jd_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
```

2. **Version on Edit Pattern:**
```python
def update(self, jd_id: int, data: dict) -> dict | None:
    with get_db() as conn:
        # Get current JD
        current = self.get(jd_id)
        if not current:
            return None

        # If raw_text changed, create version
        if data.get("raw_text") and data["raw_text"] != current["raw_text"]:
            # Get next version number
            cursor = conn.execute(
                "SELECT MAX(version_number) FROM job_description_versions WHERE job_description_id = ?",
                (jd_id,)
            )
            max_version = cursor.fetchone()[0] or 0

            # Save current as version before update
            conn.execute(
                """
                INSERT INTO job_description_versions (job_description_id, raw_text, version_number)
                VALUES (?, ?, ?)
                """,
                (jd_id, current["raw_text"], max_version + 1)
            )

        # Update JD
        # ... update query
```

---

### 2.4 Backend - Router

| File | Change Type | Description |
|------|-------------|-------------|
| `routes/job_descriptions.py` | Create | New router with 8 endpoints |
| `main.py` | Modify | Include new router |

**Endpoints:**

```python
router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])

@router.get("", response_model=list[JobDescriptionListItem])
async def list_job_descriptions():
    """List all saved JDs with preview and resume count"""

@router.post("", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(request: JobDescriptionCreate):
    """Save new JD independently"""

@router.get("/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(jd_id: int):
    """Get single JD"""

@router.put("/{jd_id}", response_model=JobDescriptionResponse)
async def update_job_description(jd_id: int, request: JobDescriptionUpdate):
    """Update JD title or text"""

@router.delete("/{jd_id}", status_code=204)
async def delete_job_description(jd_id: int):
    """Delete JD and linked resumes"""

@router.get("/{jd_id}/resumes", response_model=list[ResumeHistoryItem])
async def get_job_description_resumes(jd_id: int):
    """Get resumes linked to JD"""

# Should Have
@router.get("/{jd_id}/versions", response_model=list[JobDescriptionVersion])
async def get_job_description_versions(jd_id: int):
    """Get version history"""

@router.post("/{jd_id}/versions/{version_id}/restore", response_model=JobDescriptionResponse)
async def restore_job_description_version(jd_id: int, version_id: int):
    """Restore previous version"""
```

**main.py modification:**

```python
from routes.job_descriptions import router as job_descriptions_router

app.include_router(job_descriptions_router)
```

---

### 2.5 Backend - Resume Generator Modification

| File | Change Type | Description |
|------|-------------|-------------|
| `services/resume_generator.py` | Modify | Update generate() to set JD title from LLM result |

**Changes:**

```python
# In generate() method, after inserting job_description:
# Add title from LLM result

cursor = conn.execute(
    """
    INSERT INTO job_descriptions (raw_text, parsed_data, title, company_name)
    VALUES (?, ?, ?, ?)
    """,
    (
        job_description,
        json.dumps(llm_result.get("job_analysis", {})),
        f"{llm_result.get('job_title', 'Untitled')} at {llm_result.get('company_name', 'Unknown Company')}",
        llm_result.get('company_name'),
    ),
)
```

**Also modify delete_resume():**
```python
def delete_resume(self, resume_id: int) -> bool:
    with get_db() as conn:
        # Only delete the resume, NOT the JD
        # JD may have other resumes linked
        cursor = conn.execute("DELETE FROM generated_resumes WHERE id = ?", (resume_id,))
        conn.commit()
        return cursor.rowcount > 0
```

---

### 2.6 Frontend - API Client

| File | Change Type | Description |
|------|-------------|-------------|
| `src/lib/api.js` | Modify | Add 8 new API functions for JD CRUD |

**New Functions:**

```javascript
// Job Descriptions
export async function getJobDescriptions() {
  return request('/job-descriptions');
}

export async function createJobDescription(rawText) {
  return request('/job-descriptions', {
    method: 'POST',
    body: JSON.stringify({ raw_text: rawText })
  });
}

export async function getJobDescription(id) {
  return request(`/job-descriptions/${id}`);
}

export async function updateJobDescription(id, data) {
  return request(`/job-descriptions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteJobDescription(id) {
  return request(`/job-descriptions/${id}`, {
    method: 'DELETE'
  });
}

export async function getJobDescriptionResumes(id) {
  return request(`/job-descriptions/${id}/resumes`);
}

// Should Have
export async function getJobDescriptionVersions(id) {
  return request(`/job-descriptions/${id}/versions`);
}

export async function restoreJobDescriptionVersion(jdId, versionId) {
  return request(`/job-descriptions/${jdId}/versions/${versionId}/restore`, {
    method: 'POST'
  });
}
```

---

### 2.7 Frontend - New Components

| File | Change Type | Description |
|------|-------------|-------------|
| `src/components/SavedJobsList.svelte` | Create | Collapsible panel listing saved JDs |
| `src/components/SavedJobItem.svelte` | Create | Individual JD card with actions |

**SavedJobsList.svelte Structure:**

```svelte
<script>
  import ConfirmDialog from './ConfirmDialog.svelte';
  import SavedJobItem from './SavedJobItem.svelte';
  import { getJobDescriptions, deleteJobDescription } from '../lib/api.js';

  let { onLoad, selectedId = null } = $props();

  let jobs = $state([]);
  let loading = $state(true);
  let collapsed = $state(false);
  let deleteId = $state(null);
  let deleteResumeCount = $state(0);

  $effect(() => {
    loadJobs();
  });

  async function loadJobs() { ... }
  async function handleDelete() { ... }
  function handleLoad(id, rawText) { onLoad(id, rawText); }
  function confirmDelete(id, resumeCount) { deleteId = id; deleteResumeCount = resumeCount; }

  export function refresh() { loadJobs(); }
</script>

<div class="saved-jobs-section">
  <button class="saved-jobs-header" onclick={() => collapsed = !collapsed}>
    <h3>Saved Job Descriptions</h3>
    <span>{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="saved-jobs-content">
    {#if loading}
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
    {:else if jobs.length === 0}
      <div class="empty-state">
        <p>No saved job descriptions yet.</p>
        <p class="hint">Paste a job description above and click "Save" to keep it for later.</p>
      </div>
    {:else}
      {#each jobs as job}
        <SavedJobItem
          {job}
          selected={selectedId === job.id}
          onLoad={handleLoad}
          onDelete={confirmDelete}
        />
      {/each}
    {/if}
  </div>
  {/if}
</div>

{#if deleteId}
<ConfirmDialog
  title="Delete Job Description?"
  message={`This will also delete ${deleteResumeCount} generated resume${deleteResumeCount !== 1 ? 's' : ''} linked to this job description. This action cannot be undone.`}
  onConfirm={handleDelete}
  onCancel={() => deleteId = null}
/>
{/if}
```

**SavedJobItem.svelte Structure:**

```svelte
<script>
  import { updateJobDescription } from '../lib/api.js';

  let { job, selected = false, onLoad, onDelete } = $props();

  let editing = $state(false);
  let editTitle = $state('');

  let preview = $derived(job.raw_text_preview.slice(0, 200) + (job.raw_text_preview.length > 200 ? '...' : ''));

  function startEdit() {
    editTitle = job.title;
    editing = true;
  }

  async function saveTitle() {
    if (editTitle.trim() && editTitle !== job.title) {
      await updateJobDescription(job.id, { title: editTitle.trim() });
      job.title = editTitle.trim();
    }
    editing = false;
  }

  function cancelEdit() { editing = false; }
  function formatDate(dateStr) { ... }
</script>

<div class="saved-job-item" class:selected>
  <button
    class="job-info"
    onclick={() => onLoad(job.id, job.raw_text)}
    aria-label="{job.title}, {formatDate(job.updated_at)}, {job.resume_count} resumes. Click to load."
  >
    <div class="job-header">
      {#if editing}
        <input
          type="text"
          bind:value={editTitle}
          onkeydown={(e) => e.key === 'Enter' && saveTitle() || e.key === 'Escape' && cancelEdit()}
          onblur={saveTitle}
          class="title-input"
          maxlength="100"
        />
        <button class="icon-btn" onclick={saveTitle} aria-label="Save title">OK</button>
      {:else}
        <span class="job-title">{job.title}</span>
        <button class="icon-btn" onclick|stopPropagation={startEdit} aria-label="Edit title">Edit</button>
      {/if}
    </div>
    <p class="job-preview">{preview}</p>
    <div class="job-meta">
      <span>{formatDate(job.updated_at)}</span>
      <span>{job.resume_count} resume{job.resume_count !== 1 ? 's' : ''}</span>
    </div>
  </button>
  <button
    class="delete-link"
    onclick={() => onDelete(job.id, job.resume_count)}
    aria-label="Delete job description"
  >
    Delete
  </button>
</div>
```

---

### 2.8 Frontend - Modified Components

| File | Change Type | Description |
|------|-------------|-------------|
| `src/components/JobDescriptionInput.svelte` | Modify | Add Save button + loaded indicator |
| `src/components/ResumeGenerator.svelte` | Modify | Integrate SavedJobsList panel |

**JobDescriptionInput.svelte Changes:**

```svelte
<script>
  let {
    value = '',
    disabled = false,
    error = null,
    saving = false,
    loadedJobId = null,
    loadedJobTitle = null,
    onInput,
    onSave,
    onClear
  } = $props();

  let charCount = $derived(value.length);
  let isValid = $derived(charCount >= 100);
</script>

<div class="jd-input">
  <h2>Generate Tailored Resume</h2>
  <p class="instructions">...</p>

  {#if loadedJobId}
  <div class="loaded-indicator">
    <span class="loaded-badge">Editing: {loadedJobTitle}</span>
    <button class="clear-link" onclick={onClear}>Clear</button>
  </div>
  {/if}

  <div class="form-row">
    <label for="job-description" class="required">Job Description</label>
    <textarea ...>{value}</textarea>

    <div class="jd-meta">
      <span class="char-counter" class:valid={isValid}>
        {charCount} / 100 minimum characters
      </span>
      {#if error}
        <span class="error-message">{error}</span>
      {/if}
    </div>
  </div>

  <div class="button-row">
    <button
      class="btn"
      disabled={!isValid || disabled || saving}
      onclick={onSave}
    >
      {saving ? 'Saving...' : 'Save'}
    </button>
    <!-- Generate button remains in parent ResumeGenerator -->
  </div>
</div>
```

**ResumeGenerator.svelte Changes:**

```svelte
<script>
  import SavedJobsList from './SavedJobsList.svelte';
  // ... existing imports

  let savedJobsRef;
  let loadedJobId = $state(null);
  let loadedJobTitle = $state(null);
  let saving = $state(false);

  function handleLoadJob(id, rawText, title) {
    jobDescription = rawText;
    loadedJobId = id;
    loadedJobTitle = title;
  }

  function handleClearLoaded() {
    loadedJobId = null;
    loadedJobTitle = null;
    jobDescription = '';
  }

  async function handleSaveJob() {
    saving = true;
    try {
      if (loadedJobId) {
        await updateJobDescription(loadedJobId, { raw_text: jobDescription });
        showToast('Job description updated');
      } else {
        const result = await createJobDescription(jobDescription);
        loadedJobId = result.id;
        loadedJobTitle = result.title;
        showToast('Job description saved');
      }
      savedJobsRef?.refresh();
    } catch (e) {
      showToast('Could not save. Please try again.', 'error');
    } finally {
      saving = false;
    }
  }

  // Modify generate to refresh saved jobs
  async function generateResume() {
    // ... existing code
    savedJobsRef?.refresh();
  }
</script>

<!-- Layout -->
<JobDescriptionInput
  value={jobDescription}
  {disabled}
  {error}
  {saving}
  {loadedJobId}
  {loadedJobTitle}
  onInput={(v) => jobDescription = v}
  onSave={handleSaveJob}
  onClear={handleClearLoaded}
/>

<!-- Buttons -->
<div class="action-buttons">
  <button class="btn btn-primary" disabled={!isValid || loading} onclick={generateResume}>
    {loading ? 'Generating...' : 'Generate Resume'}
  </button>
</div>

<SavedJobsList
  bind:this={savedJobsRef}
  onLoad={(id, rawText) => handleLoadJob(id, rawText, jobs.find(j => j.id === id)?.title)}
  selectedId={loadedJobId}
/>

<ResumeHistory bind:this={historyRef} onSelect={loadResume} />
```

---

### 2.9 Frontend - Styles

| File | Change Type | Description |
|------|-------------|-------------|
| `src/styles/views/_saved-jobs.scss` | Create | Styles for SavedJobsList and SavedJobItem |
| `src/styles/views/_index.scss` | Modify | Import new SCSS file |
| `src/styles/views/_resume-generator.scss` | Modify | Add loaded-indicator styles |

**_saved-jobs.scss:**

```scss
@use "../tokens" as *;

.saved-jobs-section {
  margin-top: $spacing-section;
}

.saved-jobs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: $spacing-grid;
  background: none;
  border: 1px solid $color-border;
  border-radius: 2px;
  cursor: pointer;
  text-align: left;
  font-family: inherit;

  h3 { margin: 0; }

  &:hover { background: rgba(0, 0, 0, 0.02); }

  &:focus {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }
}

.saved-jobs-content {
  border: 1px solid $color-border;
  border-top: none;
  border-radius: 0 0 2px 2px;
}

.saved-job-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: $spacing-grid;
  border-bottom: 1px solid $color-border;

  &:last-child { border-bottom: none; }

  &.selected {
    border-left: 3px solid $color-primary;
    background: rgba($color-primary, 0.02);
  }
}

.job-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  padding: 0;

  &:hover .job-title {
    color: $color-primary;
    text-decoration: underline;
  }

  &:focus {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }
}

.job-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.job-title {
  font-weight: 600;
}

.title-input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid $color-primary;
  border-radius: 2px;
  font-family: inherit;
  font-size: inherit;

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba($color-primary, 0.2);
  }
}

.job-preview {
  margin: 0;
  font-size: 14px;
  color: rgba($color-text, 0.7);
  line-height: 1.4;
}

.job-meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: rgba($color-text, 0.6);
}

.icon-btn {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;

  &:hover { text-decoration: underline; }
}

.empty-state {
  padding: $spacing-section;
  text-align: center;
  color: rgba($color-text, 0.6);

  p { margin: 0 0 8px; }
  .hint { font-size: 14px; }
}
```

**_resume-generator.scss additions:**

```scss
.loaded-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: $spacing-grid;
  background: rgba($color-primary, 0.05);
  border-left: 3px solid $color-primary;
  border-radius: 2px;
}

.loaded-badge {
  font-size: 14px;
  color: $color-primary;
}

.clear-link {
  background: none;
  border: none;
  color: rgba($color-text, 0.6);
  cursor: pointer;
  font-size: 14px;

  &:hover {
    color: $color-text;
    text-decoration: underline;
  }
}

.button-row {
  display: flex;
  gap: $spacing-grid;
  margin-top: $spacing-grid;
}
```

---

## 3. Implementation Order

### Phase 1: Backend (MVP)
1. `database.py` - Add migrations
2. `schemas.py` - Add new models
3. `services/job_descriptions.py` - Create service
4. `routes/job_descriptions.py` - Create router
5. `main.py` - Register router
6. `services/resume_generator.py` - Modify to set JD title

### Phase 2: Frontend (MVP)
7. `src/lib/api.js` - Add API functions
8. `src/styles/views/_saved-jobs.scss` - Create styles
9. `src/styles/views/_index.scss` - Import new file
10. `src/components/SavedJobItem.svelte` - Create component
11. `src/components/SavedJobsList.svelte` - Create component
12. `src/components/JobDescriptionInput.svelte` - Add Save button + indicator
13. `src/components/ResumeGenerator.svelte` - Integrate panel
14. `src/styles/views/_resume-generator.scss` - Add indicator styles

### Phase 3: Should Have
15. Version history endpoints (backend)
16. Version history UI (frontend) - if time permits

---

## 4. Testing Strategy

### 4.1 Backend Tests

| Test File | Coverage |
|-----------|----------|
| `tests/test_job_descriptions.py` | Create, list, get, update, delete, cascade |

**Test Cases:**
- Create JD with valid text (>=100 chars)
- Create JD with invalid text (<100 chars) - expect 400
- List JDs returns correct order (newest first)
- Get single JD returns resume count
- Update title only
- Update text creates version
- Delete cascades to resumes
- Delete cascades to versions

### 4.2 Frontend Manual Tests

| Scenario | Steps |
|----------|-------|
| Save new JD | Paste JD > Click Save > Verify in list |
| Load saved JD | Click JD in list > Verify in textarea |
| Edit title | Click pencil > Type > Enter > Verify |
| Delete JD | Click Delete > Confirm > Verify removed |
| Generate updates list | Load JD > Generate > Verify resume count |

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SQLite migration fails on existing data | High | Use IF NOT EXISTS, wrap in try/except |
| Cascade delete orphans data | Low | PRAGMA foreign_keys + ON DELETE CASCADE for new tables; hybrid manual delete for legacy generated_resumes FK |
| PRAGMA not set on connection | Medium | Set in get_db() context manager (single source of truth) |
| Version history creates too much data | Low | Text is cheap; monitor if needed |

---

## 6. Dependencies

- No new npm packages required
- No new Python packages required
- Uses existing ConfirmDialog, Toast components
- Follows existing SCSS token system

---

*Ready for /v3-checklist*
