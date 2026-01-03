# Library Notes: Saved Job Descriptions

**Date:** 2026-01-03
**Libraries:** Svelte 5, FastAPI, SQLite

---

## 0. Dependencies Summary

### No New Dependencies Required

This feature uses existing project dependencies only.

**Python (requirements.txt) - Already Present:**
```
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
```

**Node.js (package.json) - Already Present:**
```json
"svelte": "^5.0.0"
```

**SQLite:** Standard library (`sqlite3`) - no additional package needed.

### Version Constraints Used

| Library | Version Constraint | Purpose |
|---------|-------------------|---------|
| Svelte | ^5.0.0 | Runes ($state, $derived, $effect, $props) |
| FastAPI | >=0.100.0 | APIRouter, HTTPException, response_model |
| Pydantic | >=2.0 | BaseModel, Field, field_validator |
| sqlite3 | stdlib | PRAGMA foreign_keys, ON DELETE CASCADE |

---

## 1. Svelte 5 Patterns (from context7)

### 1.1 Reactive State with $state

```javascript
let count = $state(0);
let history = $state([]);
let loading = $state(true);
```

### 1.2 Derived State with $derived

```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);

  // For feature: character count validation
  let charCount = $derived(value.length);
  let isValid = $derived(charCount >= 100);
</script>
```

### 1.3 Side Effects with $effect

```javascript
$effect(() => {
  // Runs after DOM updates when dependencies change
  console.log('The count is now ' + count);
});

// Cleanup pattern
$effect(() => {
  const handler = () => {};
  return () => {
    // cleanup code runs before next effect or on unmount
  };
});
```

### 1.4 Props Declaration with $props

```svelte
<script>
  // Destructuring with defaults
  let { optional = 'unset', required } = $props();

  // Callback props (replaces createEventDispatcher)
  let { onSelect, onDelete } = $props();
</script>
```

### 1.5 Component Events via Callback Props

```svelte
<!-- Parent: -->
<SavedJobItem
  onLoad={(id) => loadJob(id)}
  onDelete={(id) => deleteJob(id)}
/>

<!-- Child: -->
<script>
  let { onLoad, onDelete } = $props();
</script>
<button onclick={() => onLoad(item.id)}>Load</button>
```

---

## 2. FastAPI Patterns (from context7)

### 2.1 Router Definition

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])
```

### 2.2 Pydantic Models for Request/Response

```python
from pydantic import BaseModel, Field

class JobDescriptionCreate(BaseModel):
    raw_text: str = Field(..., min_length=100)

class JobDescriptionUpdate(BaseModel):
    title: str | None = None
    raw_text: str | None = None

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    raw_text: str
    company_name: str | None
    created_at: str
    updated_at: str
    resume_count: int
```

### 2.3 CRUD Endpoints Pattern

```python
@router.get("", response_model=list[JobDescriptionResponse])
async def list_job_descriptions():
    # Returns all saved JDs
    pass

@router.post("", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(data: JobDescriptionCreate):
    # Creates new JD
    pass

@router.get("/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(jd_id: int):
    jd = service.get(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd

@router.put("/{jd_id}", response_model=JobDescriptionResponse)
async def update_job_description(jd_id: int, data: JobDescriptionUpdate):
    jd = service.update(jd_id, data)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd

@router.delete("/{jd_id}", status_code=204)
async def delete_job_description(jd_id: int):
    deleted = service.delete(jd_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job description not found")
    return None
```

---

## 3. SQLite Patterns (Project-specific)

### 3.1 Database Access Pattern with PRAGMA

```python
# From database.py - use context manager with PRAGMA
from database import get_db

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")  # Required for FK cascade
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_db() as conn:
    cursor = conn.execute("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,))
    row = cursor.fetchone()
    conn.commit()
```

### 3.2 SQLite ALTER TABLE Limitations

```sql
-- SQLite doesn't support DEFAULT CURRENT_TIMESTAMP in ALTER TABLE
-- Use NULL default, then UPDATE to backfill

ALTER TABLE job_descriptions ADD COLUMN updated_at TEXT;
UPDATE job_descriptions SET updated_at = created_at WHERE updated_at IS NULL;
```

### 3.3 Foreign Key Cascade (Best Practice)

**PRAGMA foreign_keys = ON** is the recommended approach per [SQLite docs](https://sqlite.org/foreignkeys.html):
- Must be set on **every connection** (not just init)
- Set it in get_db() context manager
- Define FK with ON DELETE CASCADE in CREATE TABLE

```sql
-- New tables: use FK CASCADE
CREATE TABLE job_description_versions (
    id INTEGER PRIMARY KEY,
    job_description_id INTEGER NOT NULL,
    FOREIGN KEY (job_description_id)
        REFERENCES job_descriptions(id) ON DELETE CASCADE
);
```

```python
# For legacy FK without CASCADE (generated_resumes), use hybrid:
def delete_job_description(jd_id: int) -> bool:
    with get_db() as conn:
        # Manual delete for legacy FK
        conn.execute(
            "DELETE FROM generated_resumes WHERE job_description_id = ?",
            (jd_id,)
        )
        # New tables with CASCADE auto-delete
        cursor = conn.execute(
            "DELETE FROM job_descriptions WHERE id = ?",
            (jd_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
```

---

## 4. Existing Project Patterns

### 4.1 Svelte Component Structure (ResumeHistory.svelte)

```svelte
<script>
  import ConfirmDialog from './ConfirmDialog.svelte';
  import { getResumes, deleteResume } from '../lib/api.js';

  let { onSelect } = $props();

  let history = $state([]);
  let loading = $state(true);
  let collapsed = $state(false);
  let deleteId = $state(null);

  $effect(() => {
    loadData();
  });

  async function loadData() {
    try {
      history = await getResumes();
    } catch (e) {
      console.error('Failed to load:', e);
    } finally {
      loading = false;
    }
  }

  // Expose refresh method
  export function refresh() {
    loadData();
  }
</script>

<!-- Collapsible section pattern -->
<div class="history-section">
  <button class="history-header" onclick={() => collapsed = !collapsed}>
    <h3>Title</h3>
    <span>{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="history-content">
    {#if loading}
      <div class="skeleton"></div>
    {:else if items.length === 0}
      <p class="empty-state">Empty message</p>
    {:else}
      <!-- List items -->
    {/if}
  </div>
  {/if}
</div>

{#if deleteId}
<ConfirmDialog
  title="Title"
  message="Message"
  onConfirm={handleDelete}
  onCancel={() => deleteId = null}
/>
{/if}
```

### 4.2 API Client Pattern (api.js)

```javascript
const API_BASE = '/api';

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  if (response.status === 204) return null;
  return response.json();
}

// CRUD pattern
export async function getItems() {
  return request('/items');
}

export async function createItem(data) {
  return request('/items', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateItem(id, data) {
  return request(`/items/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteItem(id) {
  return request(`/items/${id}`, { method: 'DELETE' });
}
```

### 4.3 FastAPI Route Pattern (routes/resumes.py)

```python
from fastapi import APIRouter, HTTPException
from schemas import RequestModel, ResponseModel
from services.service_name import service_instance

router = APIRouter(prefix="/api/resource", tags=["resource"])

@router.post("", response_model=ResponseModel)
async def create(request: RequestModel):
    try:
        return service_instance.create(request)
    except SomeError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 4.4 SCSS Pattern (views/_history.scss)

```scss
@use "../tokens" as *;

.section-name {
  margin-top: $spacing-section;
}

.header-button {
  display: flex;
  justify-content: space-between;
  padding: $spacing-grid;
  border: 1px solid $color-border;
  cursor: pointer;

  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }

  &:focus {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }
}

.item {
  padding: $spacing-grid;
  border-bottom: 1px solid $color-border;

  &:last-child {
    border-bottom: none;
  }
}
```

---

## 5. Key Implementation Notes

### 5.1 Svelte 5 Migration Notes
- Use `$state()` instead of `let x`
- Use `$derived()` instead of `$:` reactive statements
- Use `$effect()` instead of `$:` for side effects
- Use `$props()` instead of `export let`
- Use callback props instead of `createEventDispatcher`
- Use `onclick` instead of `on:click`

### 5.2 Database Notes
- Enable foreign keys: `PRAGMA foreign_keys = ON` in get_db() context manager
- New tables: use ON DELETE CASCADE in FK definition
- Legacy tables: hybrid approach (manual delete for old FKs without CASCADE)
- Use `conn.execute()` with parameterized queries for SQL injection prevention

### 5.3 Error Handling Notes
- FastAPI: Use `HTTPException` for API errors
- Svelte: Use try/catch in async functions, log with `console.error`
- Show user-friendly messages via Toast component

---

*Research Complete | Ready for /v3-design*
