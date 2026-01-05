# Library Notes: Import JSON Profile

**Date:** 2026-01-04
**Purpose:** Ecosystem prerequisites and syntax reference for JSON profile import feature

---

## 0. Ecosystem Prerequisites

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Already configured in `.python-version`, all dependencies support it |
| Node.js | >=20.0.0 <21.0.0 | Already configured in `package.json` engines |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python version + venv + packages | `uv --version` |
| npm | Node.js package management | `npm --version` |

### No Setup Changes Required
The existing environment supports all libraries needed for this feature. No version upgrades or new dependencies required.

---

## 1. Svelte 5

**Version Constraint:** `svelte@^5.0.0` (already in package.json)

### Correct Patterns (Svelte 5 Runes)

#### State Declaration
```svelte
<script>
  let isOpen = $state(false);
  let fileData = $state(null);
  let errors = $state([]);
</script>
```

#### Props Declaration
```svelte
<script>
  let { onClose, onImport } = $props();
</script>
```

#### Effects (Reactive Side Effects)
```svelte
<script>
  $effect(() => {
    if (dialogRef) {
      dialogRef.focus();
    }
  });
</script>
```

#### Event Handling (Callback Props Pattern)
```svelte
<!-- Parent component -->
<ImportModal
  onClose={() => showModal = false}
  onImport={(data) => handleImport(data)}
/>

<!-- Child component -->
<script>
  let { onClose, onImport } = $props();
</script>
<button onclick={onClose}>Cancel</button>
<button onclick={() => onImport(data)}>Import</button>
```

### Deprecated (Avoid)
- `createEventDispatcher()` → Use callback props instead
- `on:click` directive on components → Use `onclick` callback prop
- `export let prop` → Use `let { prop } = $props()`
- `$:` reactive statements → Use `$derived()` or `$effect()`

### File Input Pattern (from PhotoUpload.svelte)
```svelte
<input
  type="file"
  id="json-input"
  accept=".json"
  onchange={handleFileSelect}
  hidden
/>

<script>
  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      processFile(file);
    }
    e.target.value = ''; // Reset for re-selection
  }
</script>
```

### Drag-Drop Pattern (from PhotoUpload.svelte)
```svelte
<div
  class="drop-zone"
  class:drag-over={isDragOver}
  ondragover={handleDragOver}
  ondragleave={handleDragLeave}
  ondrop={handleDrop}
  role="button"
  tabindex="0"
>

<script>
  function handleDragOver(e) {
    e.preventDefault();
    isDragOver = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    isDragOver = false;
  }

  function handleDrop(e) {
    e.preventDefault();
    isDragOver = false;
    const file = e.dataTransfer?.files[0];
    if (file) processFile(file);
  }
</script>
```

---

## 2. Pydantic v2

**Version Constraint:** `pydantic>=2.0` (already in requirements.txt)

### Correct Patterns

#### Nested Models with Optional Fields
```python
from typing import Optional
from pydantic import BaseModel

class Foo(BaseModel):
    count: int
    size: Optional[float] = None

class Spam(BaseModel):
    foo: Foo
    bars: list[Bar]

# Automatic nested validation from dict
m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}])
```

#### Required vs Optional Fields (Pydantic v2)
```python
from pydantic import BaseModel

class Foo(BaseModel):
    f1: str                    # required, cannot be None
    f2: str | None             # required, CAN be None
    f3: str | None = None      # not required, can be None
    f4: str = 'Foobar'         # not required, cannot be None
```

#### Field Validator
```python
from pydantic import BaseModel, field_validator

class WorkExperienceImport(BaseModel):
    company: str
    title: str
    start_date: str

    @field_validator("start_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Invalid date format. Use YYYY-MM")
        return v
```

#### Model Validator (Cross-Field Validation)
```python
from pydantic import BaseModel, model_validator
from typing import Self

class ProfileImport(BaseModel):
    personal_info: PersonalInfoImport
    work_experiences: list[WorkExperienceImport]

    @model_validator(mode='after')
    def validate_profile(self) -> Self:
        # Cross-field validation logic
        return self
```

### Deprecated (Avoid)
- `@validator` → Use `@field_validator`
- `@root_validator` → Use `@model_validator`
- `class Config:` → Use `model_config = ConfigDict(...)`

---

## 3. FastAPI

**Version Constraint:** `fastapi>=0.100.0` (already in requirements.txt)

### Correct Patterns

#### PUT Endpoint with Pydantic Model
```python
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["profile"])

class ProfileImport(BaseModel):
    personal_info: PersonalInfoImport
    work_experiences: list[WorkExperienceImport]
    # ...

@router.put("/profile/import")
async def import_profile(profile: ProfileImport):
    # Pydantic automatically validates request body
    # Clear existing data and insert new
    return {"message": "Profile imported successfully"}
```

#### Error Response Pattern
```python
from fastapi import HTTPException

@router.put("/profile/import")
async def import_profile(profile: ProfileImport):
    try:
        # Import logic
        return {"message": "Profile imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Existing Project Patterns (from routes/)
```python
# From routes/personal_info.py pattern
@router.put("/personal-info")
async def update_personal_info(data: PersonalInfoUpdate):
    conn = get_db()
    # ... database operations
    return result
```

---

## 4. Browser File API (Native JavaScript)

**No package required** - Built into browsers

### FileReader for JSON
```javascript
function readJsonFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result);
        resolve(data);
      } catch (e) {
        reject(new Error(`Invalid JSON: ${e.message}`));
      }
    };
    reader.onerror = () => reject(new Error('Could not read file'));
    reader.readAsText(file);
  });
}
```

### File Download (Sample JSON)
```javascript
function downloadSampleJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

---

## 5. Frontend Validation Pattern

### JSON Schema Validation (Manual)
```javascript
function validateProfileJson(data) {
  const errors = [];

  // Required sections
  if (!data.personal_info) {
    errors.push('Missing required section: personal_info');
  }

  // Required fields
  if (!data.personal_info?.full_name) {
    errors.push('Missing required field: personal_info.full_name');
  }

  // Type validation
  if (data.education) {
    data.education.forEach((edu, i) => {
      if (edu.graduation_year !== undefined && typeof edu.graduation_year !== 'number') {
        errors.push(`Invalid type: education[${i}].graduation_year must be a number`);
      }
    });
  }

  return errors;
}
```

---

## Dependencies Summary

**No changes required to requirements.txt or package.json**

All libraries are already at compatible versions:
- `svelte@^5.0.0` - Svelte 5 runes supported
- `pydantic>=2.0` - v2 validation patterns
- `fastapi>=0.100.0` - Modern endpoint patterns

---

## Key Implementation Notes

1. **Svelte 5 Runes:** Use `$state`, `$props`, `$effect` - not legacy syntax
2. **Pydantic v2:** Use `field_validator`, `model_validator` - not v1 decorators
3. **Callback Props:** Pass functions as props for component events, not `createEventDispatcher`
4. **File Handling:** Use FileReader API for JSON parsing, handle errors gracefully
5. **Atomic Import:** Backend should clear + insert in single transaction

---

*Reference for /v4-design and /v4-checklist*
