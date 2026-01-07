# Library Research Notes: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language

## Existing Ecosystem Summary

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.13 | `.python-version` |
| Node | 20 | `.nvmrc`, engines: >=20.0.0 <21.0.0 |
| FastAPI | >=0.100.0 | API framework |
| Pydantic | >=2.0 | Data validation |
| Svelte | ^5.0.0 | Frontend framework |
| SQLite | Built-in | Database (no ORM) |

## Runtime Version Decision

**Decision:** Respect existing versions (Option A)
**Rationale:** All existing libraries fully support the feature requirements. No new dependencies needed.

## Libraries Researched

### 1. Pydantic 2 - CEFR Enum Validation

**Version Constraint:** `>=2.0` (existing)

**Correct Pattern - String Enum:**
```python
from enum import Enum
from pydantic import BaseModel

class CEFRLevel(str, Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

class LanguageCreate(BaseModel):
    name: str
    level: CEFRLevel
```

**Key Points:**
- `str, Enum` inheritance allows JSON serialization as string value
- Pydantic 2 automatically validates against enum members
- Invalid values return 422 with message: `Input should be 'A1', 'A2', 'B1', 'B2', 'C1' or 'C2'`

**Deprecated Patterns to Avoid:**
- Using `Literal['A1', 'A2', ...]` - works but loses enum semantics
- Using `@validator` decorator (Pydantic v1) - use `@field_validator` in v2

### 2. FastAPI - CRUD Endpoints

**Version Constraint:** `>=0.100.0` (existing)

**Correct Pattern - Full CRUD with APIRouter:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/languages", tags=["languages"])

@router.get("", response_model=list[Language])
async def list_languages():
    ...

@router.post("", response_model=Language)
async def create_language(lang: LanguageCreate):
    ...

@router.put("/{lang_id}", response_model=Language)
async def update_language(lang_id: int, lang: LanguageUpdate):
    ...

@router.delete("/{lang_id}")
async def delete_language(lang_id: int):
    ...
```

**Key Points:**
- Use `response_model` for automatic serialization/validation
- Path parameters automatically parsed as specified type
- Return 404 HTTPException for missing resources
- Use `model_validate(dict(row))` for SQLite Row → Pydantic model

**Existing Codebase Patterns (from `routes/education.py`):**
- GET list returns `list[Model]`
- POST returns created `Model`
- PUT returns updated `Model`
- DELETE returns `{"deleted": id}`

### 3. Svelte 5 - Event Handling & Drag-and-Drop

**Version Constraint:** `^5.0.0` (existing)

**Correct Pattern - Svelte 5 Event Handlers:**
```svelte
<script>
  let count = $state(0);

  function onclick() {
    count++;
  }
</script>

<button {onclick}>clicks: {count}</button>
```

**Key Points:**
- Events are properties, not directives: `onclick` not `on:click`
- Use `$state()` for reactive state
- Use `$effect()` for side effects (like data fetching on mount)
- Callback props replace `createEventDispatcher`

**Drag-and-Drop Pattern (Native HTML5):**
```svelte
<script>
  let items = $state([...]);
  let draggedIndex = $state(null);

  function ondragstart(e, index) {
    draggedIndex = index;
    e.dataTransfer.effectAllowed = 'move';
  }

  function ondragover(e) {
    e.preventDefault();
  }

  function ondrop(e, dropIndex) {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) return;

    const newItems = [...items];
    const [dragged] = newItems.splice(draggedIndex, 1);
    newItems.splice(dropIndex, 0, dragged);
    items = newItems;
    draggedIndex = null;
    // Persist new order via API
  }
</script>

{#each items as item, index}
  <div
    draggable="true"
    ondragstart={(e) => ondragstart(e, index)}
    ondragover={ondragover}
    ondrop={(e) => ondrop(e, index)}
  >
    {item.name}
  </div>
{/each}
```

**Key Points:**
- Use `draggable="true"` attribute
- `ondragstart`, `ondragover`, `ondrop` are property names (Svelte 5)
- Prevent default on `dragover` to allow drop
- Update local state immediately, then persist via API

**Existing Codebase Patterns (from `Education.svelte`):**
- `$state([])` for item arrays
- `$state(null)` for editingId, confirmDelete
- `$effect()` for initial data load
- `export function add()` for parent-triggered actions
- ConfirmDialog component for delete confirmation

### 4. SQLite - Table Schema

**Pattern for Languages Table:**
```sql
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Key Points:**
- CHECK constraint for enum validation at DB level
- `display_order` INTEGER for drag-and-drop ordering
- Follow existing pattern: `created_at`, `updated_at` timestamps

## Deprecated Patterns to Avoid

| Pattern | Why Avoid | Use Instead |
|---------|-----------|-------------|
| `on:click` directive | Svelte 4 syntax | `onclick` property |
| `createEventDispatcher` | Svelte 4 | Callback props |
| Pydantic `@validator` | v1 syntax | `@field_validator` |
| `Literal` for enums | Loses type semantics | `str, Enum` class |

## Dependencies Summary

**No new dependencies required.**

All functionality can be implemented with existing stack:
- Python 3.13
- FastAPI >=0.100.0
- Pydantic >=2.0
- Svelte ^5.0.0
- SQLite (built-in)

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Ecosystem preference | A - Respect existing versions | No dependency changes needed |

## Next

Proceed to `/v5-design`
