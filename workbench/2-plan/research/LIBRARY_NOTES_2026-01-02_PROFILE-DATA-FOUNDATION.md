# Library Notes: Profile Data Foundation

**Date:** 2026-01-02
**Purpose:** Ecosystem prerequisites and syntax reference for implementation

---

## 0. Ecosystem Prerequisites

### Runtime Version Selection (from context7 lookups)

| Step | Action | Result |
|------|--------|--------|
| 1 | Latest stable Python? | 3.14 (context7 shows full docs) |
| 2 | FastAPI supports 3.14? | ✓ (explicitly mentions 3.14 + Pydantic v2) |
| 3 | Pydantic v2 supports 3.14? | ✓ (FastAPI docs confirm) |
| 4 | Uvicorn supports 3.14? | ✗ (only "officially supports Python 3.13" per v0.32.0 release notes) |
| 5 | Step down → Python 3.13 | All libraries support 3.13 ✓ |

**Decision: Python 3.13**

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Highest version with explicit support from all libraries (FastAPI, Pydantic v2, Uvicorn) |
| Node.js | 20 LTS | Svelte 5 and Rollup require modern Node; 20 is current LTS |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python version + venv + packages | `uv --version` |
| nvm | Node version management | `nvm --version` |
| npm | Node package management | `npm --version` |

### Setup Commands

**Python (Backend):**
```bash
uv python install 3.13
uv python pin 3.13
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Node (Frontend):**
```bash
nvm install 20
nvm use 20
echo "20" > .nvmrc
npm install
```

---

## Pydantic

**Version Constraint:** `pydantic>=2.0`

### Correct Patterns (Pydantic v2)

- `model_config = ConfigDict(from_attributes=True)` for ORM mode
- `.model_validate(obj)` to create model from dict/ORM object
- `.model_dump()` to convert model to dict
- `.model_dump_json()` to serialize directly to JSON string
- `str | None = None` for optional fields (not required, can be None)
- `str | None` for required fields that can be None
- `Field(default=...)` for defaults with metadata

### Deprecated (Avoid - Pydantic v1 syntax)

- `class Config: orm_mode = True` → Use `model_config = ConfigDict(from_attributes=True)`
- `.from_orm()` → Use `.model_validate()`
- `.dict()` → Use `.model_dump()`
- `.json()` → Use `.model_dump_json()`
- `Optional[str]` → Use `str | None` (Python 3.10+ syntax)

### Code Examples

```python
from pydantic import BaseModel, ConfigDict, Field

class WorkExperience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    title: str
    start_date: str  # YYYY-MM format
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    location: str | None = None

# Create from dict
exp = WorkExperience.model_validate({
    "id": 1,
    "company": "Acme Corp",
    "title": "Developer",
    "start_date": "2020-01"
})

# Convert to dict
data = exp.model_dump()

# Convert to dict excluding unset fields
data = exp.model_dump(exclude_unset=True)

# Convert to JSON string
json_str = exp.model_dump_json()
```

### Validation

```python
from pydantic import BaseModel, ValidationError

class PersonalInfo(BaseModel):
    full_name: str  # required, cannot be None
    email: str      # required, cannot be None
    phone: str | None = None  # not required, can be None
    location: str | None = None

try:
    info = PersonalInfo.model_validate({"full_name": "", "email": "test@example.com"})
except ValidationError as e:
    print(e)  # Validation errors
```

---

## FastAPI

**Version Constraint:** `fastapi>=0.100.0`

### Correct Patterns

- Use Pydantic models for request bodies (auto-validated)
- Path parameters: `@app.get("/items/{item_id}")`
- Request body: Function parameter with Pydantic model type
- Query parameters: Function parameter with simple type + default
- Response model: `response_model=ModelClass` in decorator
- Use `async def` for route handlers

### CRUD Endpoint Patterns

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None

# CREATE
@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate):
    # item is auto-validated Pydantic model
    result = {"id": 1, **item.model_dump()}
    return result

# READ (single)
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    # item_id is auto-converted to int
    return {"id": item_id, "name": "Example"}

# READ (list)
@app.get("/items/", response_model=list[Item])
async def list_items():
    return [{"id": 1, "name": "Example"}]

# UPDATE
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    return {"item_id": item_id, **item.model_dump()}

# DELETE
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": item_id}
```

### Static Files

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files from 'static' directory at '/static' URL path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html from 'public' directory
app.mount("/", StaticFiles(directory="public", html=True), name="public")
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]
```

---

## Uvicorn

**Version Constraint:** `uvicorn>=0.32.0`

### Why This Version

- v0.32.0 (October 2024): "Officially support Python 3.13"
- v0.34.0 (December 2024): "Drop support for Python 3.8"

### Usage

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

---

## SQLite (Python stdlib)

**Version Constraint:** Built-in (no pip install needed)

### Correct Patterns

```python
import sqlite3
from contextlib import contextmanager

DATABASE = "app.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_db() as conn:
    cursor = conn.execute("SELECT * FROM work_experiences")
    rows = cursor.fetchall()
    # Access as dict: row["company"], row["title"]

    # Insert with parameters (prevents SQL injection)
    conn.execute(
        "INSERT INTO work_experiences (company, title) VALUES (?, ?)",
        (company, title)
    )
    conn.commit()
```

### Schema Initialization

```python
def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY DEFAULT 1,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                location TEXT,
                linkedin_url TEXT,
                summary TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK (id = 1)
            );
        """)
```

---

## Svelte

**Version Constraint:** `svelte@^5.0.0` (Svelte 5 with runes)

### Correct Patterns (Svelte 5 Runes)

- `$state(initialValue)` for reactive state
- `$derived(expression)` for computed values
- `$effect(() => { ... })` for side effects
- `onclick={handler}` for events (no colon!)
- `bind:value={variable}` for two-way binding

### Deprecated (Avoid - Svelte 4 syntax)

- `let count = 0` for state → Use `let count = $state(0)`
- `$: doubled = count * 2` → Use `let doubled = $derived(count * 2)`
- `$: { console.log(count) }` → Use `$effect(() => { console.log(count) })`
- `on:click={handler}` → Use `onclick={handler}`

### Code Examples

**Basic State and Events:**
```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);

  $effect(() => {
    console.log('Count changed:', count);
  });
</script>

<button onclick={() => count++}>Clicked: {count}</button>
<p>Doubled: {doubled}</p>
```

**Form Input Binding:**
```svelte
<script>
  let name = $state('');
  let email = $state('');
  let accepted = $state(false);
</script>

<input bind:value={name} placeholder="Name" />
<input type="email" bind:value={email} placeholder="Email" />
<label>
  <input type="checkbox" bind:checked={accepted} />
  Accept terms
</label>
```

**Number Input (auto-coerced):**
```svelte
<script>
  let year = $state(2024);
</script>

<input type="number" bind:value={year} min="1900" max="2100" />
```

**Fetch API Call:**
```svelte
<script>
  let data = $state(null);
  let loading = $state(false);
  let error = $state(null);

  async function fetchData() {
    loading = true;
    error = null;
    try {
      const res = await fetch('/api/items');
      if (!res.ok) throw new Error('Failed to fetch');
      data = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function saveData(item) {
    const res = await fetch('/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    });
    if (!res.ok) throw new Error('Failed to save');
    return res.json();
  }
</script>
```

**Conditional Rendering:**
```svelte
{#if loading}
  <p>Loading...</p>
{:else if error}
  <p class="error">{error}</p>
{:else if data}
  <ul>
    {#each data as item}
      <li>{item.name}</li>
    {/each}
  </ul>
{:else}
  <p>No data yet</p>
{/if}
```

---

## Rollup

**Version Constraint:** `rollup@^4.0.0`

### Correct Configuration for Svelte

```javascript
// rollup.config.js
import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';
import css from 'rollup-plugin-css-only';

const production = !process.env.ROLLUP_WATCH;

export default {
  input: 'src/main.js',
  output: {
    sourcemap: true,
    format: 'iife',
    name: 'app',
    file: 'public/build/bundle.js'
  },
  plugins: [
    svelte({
      compilerOptions: {
        dev: !production
      }
    }),
    css({ output: 'bundle.css' }),
    resolve({
      browser: true,
      dedupe: ['svelte']
    }),
    commonjs(),
    production && terser()
  ],
  watch: {
    clearScreen: false
  }
};
```

### Required Plugins (npm packages)

- `rollup-plugin-svelte` - Compile Svelte components
- `@rollup/plugin-node-resolve` - Resolve node_modules
- `@rollup/plugin-commonjs` - Convert CommonJS to ES modules
- `@rollup/plugin-terser` - Minification (production)
- `rollup-plugin-css-only` - Extract CSS to separate file

---

## Dart Sass

**Version Constraint:** `sass@^1.80.0`

### Setup

Sass compiles at build time via npm script, not bundled by Rollup.

```json
{
  "scripts": {
    "build:css": "sass src/styles/main.scss:public/build/global.css --style=compressed",
    "watch:css": "sass src/styles/main.scss:public/build/global.css --watch"
  }
}
```

---

## Dependencies Summary

**COPY TO requirements.txt:**

```
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
```

**COPY TO package.json devDependencies:**

```json
{
  "devDependencies": {
    "svelte": "^5.0.0",
    "rollup": "^4.0.0",
    "rollup-plugin-svelte": "^7.2.0",
    "@rollup/plugin-node-resolve": "^15.0.0",
    "@rollup/plugin-commonjs": "^25.0.0",
    "@rollup/plugin-terser": "^0.4.0",
    "rollup-plugin-css-only": "^4.5.0",
    "sass": "^1.80.0"
  }
}
```

---

## Browser Compatibility Note

`<input type="month">` has poor Safari support. Implementation should:
1. Use `<input type="month">` as primary
2. Fall back to `<input type="text" placeholder="YYYY-MM">` with pattern validation if unsupported
3. Or use simple text input with format hint

---

*Reference for /v3-design and /v3-checklist*
