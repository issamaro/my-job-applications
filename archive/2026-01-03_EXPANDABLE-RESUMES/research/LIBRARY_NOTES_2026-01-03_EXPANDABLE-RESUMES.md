# Library Notes: My Job Applications (Unified View)

**Date:** 2026-01-03
**Purpose:** Ecosystem prerequisites and syntax reference for implementation

---

## 0. Ecosystem Prerequisites

### Runtime (from context7 lookups)

| Runtime | Version | Reason |
|---------|---------|--------|
| Node.js | 20.x | Required by package.json `engines` field |
| Python | 3.13+ | User-specified requirement |

### Tooling

| Tool | Purpose | Verify |
|------|---------|--------|
| nvm | Node version management | `nvm --version` |
| npm | Package management | `npm --version` |
| uv | Python version + venv + packages | `uv --version` |

### Setup Commands

```bash
# Frontend
nvm use 20
npm install

# Backend
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## 1. Svelte 5

**Version Constraint:** `svelte>=5.0.0` (already in package.json)

### Correct Patterns (Svelte 5 Runes)

#### State Declaration
```svelte
<script>
  // Reactive state with $state rune
  let expanded = $state(false);
  let resumes = $state([]);
  let loading = $state(false);
</script>
```

#### Derived State
```svelte
<script>
  // Computed values with $derived
  let preview = $derived(
    job.raw_text_preview.length > 200
      ? job.raw_text_preview.slice(0, 200) + '...'
      : job.raw_text_preview
  );
</script>
```

#### Props Declaration
```svelte
<script>
  // Props with $props rune (destructuring with defaults)
  let { job, selected = false, onLoad, onDelete, onSelectResume } = $props();
</script>
```

#### Event Handlers
```svelte
<!-- Svelte 5 uses lowercase onclick (not on:click) -->
<button onclick={() => expanded = !expanded}>Toggle</button>

<!-- Event with stopPropagation -->
<button onclick={(e) => { e.stopPropagation(); handleClick(); }}>Click</button>
```

#### Effects (Side Effects)
```svelte
<script>
  // Run on mount and when dependencies change
  $effect(() => {
    loadResumes();
  });
</script>
```

#### Await Block for Async Loading
```svelte
{#await promise}
  <!-- Pending state -->
  <div class="skeleton"></div>
{:then data}
  <!-- Resolved state -->
  {#each data as item}
    <div>{item.name}</div>
  {/each}
{:catch error}
  <!-- Error state -->
  <p>Error: {error.message}</p>
{/await}
```

#### Conditional Rendering
```svelte
{#if expanded}
  <div class="resume-list">...</div>
{/if}

<!-- With else -->
{#if loading}
  <span class="spinner"></span>
{:else if resumes.length === 0}
  <p>No resumes</p>
{:else}
  {#each resumes as resume}...{/each}
{/if}
```

#### ARIA for Expand/Collapse
```svelte
<button
  onclick={() => expanded = !expanded}
  aria-expanded={expanded}
  aria-controls="resume-list-{job.id}"
>
  {expanded ? '[-]' : '[+]'}
</button>

{#if expanded}
  <div id="resume-list-{job.id}" role="list">
    ...
  </div>
{/if}
```

### Deprecated (Avoid)

| Old Svelte 4 | New Svelte 5 |
|--------------|--------------|
| `let count = 0;` (reactive) | `let count = $state(0);` |
| `$: derived = x + y;` | `let derived = $derived(x + y);` |
| `export let prop;` | `let { prop } = $props();` |
| `on:click={handler}` | `onclick={handler}` |
| `$: { sideEffect(); }` | `$effect(() => { sideEffect(); });` |

### Codebase Patterns (Existing)

From `SavedJobItem.svelte` and `ResumeHistory.svelte`:
```svelte
// State
let editing = $state(false);
let collapsed = $state(false);
let deleteId = $state(null);

// Props
let { job, selected = false, onLoad, onDelete } = $props();

// Effect for loading
$effect(() => {
  loadHistory();
});

// Event handler
onclick={() => collapsed = !collapsed}

// ARIA
aria-expanded={!collapsed}
```

---

## 2. FastAPI

**Version Constraint:** `fastapi>=0.100.0` (already in requirements.txt)

### Correct Patterns

#### Optional Request Body Field
```python
from pydantic import BaseModel

class ResumeGenerateRequest(BaseModel):
    job_description: str
    job_description_id: int | None = None  # Optional field
```

#### Endpoint with Optional Body Parameter
```python
@app.post("/resumes/generate")
async def generate_resume(request: ResumeGenerateRequest):
    if request.job_description_id is not None:
        # Link to existing JD
        pass
    else:
        # Create new JD (existing behavior)
        pass
```

### Deprecated (Avoid)

| Old | New |
|-----|-----|
| `Union[str, None]` | `str \| None` |
| `Optional[str]` without default | `str \| None = None` |

---

## 3. Pydantic v2

**Version Constraint:** `pydantic>=2.0` (already in requirements.txt)

### Correct Patterns

#### Optional Fields with Default None
```python
from pydantic import BaseModel

class ResumeGenerateRequest(BaseModel):
    job_description: str                    # Required
    job_description_id: int | None = None   # Not required, can be None
    personal_data: dict | None = None       # Not required, can be None
```

#### Field Semantics in Pydantic v2
```python
# Required, cannot be None
field: str

# Required, CAN be None (must provide explicitly)
field: str | None

# NOT required, can be None (has default)
field: str | None = None

# NOT required, cannot be None (has non-None default)
field: str = "default"
```

#### Model Methods
```python
# Convert to dict
data = model.model_dump()

# Validate from dict/ORM
instance = MyModel.model_validate(data)
```

### Deprecated (Avoid)

| Pydantic v1 | Pydantic v2 |
|-------------|-------------|
| `.dict()` | `.model_dump()` |
| `.from_orm()` | `.model_validate()` |
| `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `Optional[str]` (ambiguous) | `str \| None = None` (explicit) |

---

## 4. Project-Specific APIs (Already Exist)

### Frontend API Functions (src/lib/api.js)

| Function | Purpose | Used By |
|----------|---------|---------|
| `getJobDescriptionResumes(id)` | Fetch resumes for a job | NEW: SavedJobItem |
| `deleteResume(id)` | Delete a resume | ResumeHistory -> SavedJobItem |
| `getResume(id)` | Get resume details | ResumeHistory -> SavedJobItem |
| `updateJobDescription(id, data)` | Update JD title | SavedJobItem |

### Backend Endpoints (Already Exist)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/job-descriptions/{id}/resumes` | GET | Get resumes for a JD |
| `/resumes/{id}` | DELETE | Delete a resume |
| `/resumes/generate` | POST | Generate resume (needs modification) |

---

## 5. CSS/SCSS Patterns

### Existing Class Conventions (from _saved-jobs.scss)

```scss
// Component block
.saved-job-item { }

// Nested elements
.saved-job-item .job-header { }
.saved-job-item .job-meta { }

// State modifiers
.saved-job-item.selected { }
.saved-job-item.expanded { }
```

### New Classes Needed

```scss
// Resume list inside job item
.saved-job-item .resume-list { }
.saved-job-item .resume-item { }
.saved-job-item .resume-meta { }

// Expand toggle
.saved-job-item .expand-toggle { }
.saved-job-item .expand-toggle[aria-expanded="true"] { }
```

---

## Dependencies Summary

**Already in requirements.txt (no changes needed):**
```
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
```

**Already in package.json (no changes needed):**
```json
{
  "svelte": "^5.0.0"
}
```

No new dependencies required for this feature.

---

*Reference for /v3-design and /v3-checklist*
