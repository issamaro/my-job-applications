# Library Notes: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Purpose:** Ecosystem prerequisites and syntax reference for implementation

---

## 0. Ecosystem Prerequisites

### Runtime (Already Configured)

| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Already set in `.python-version`; Anthropic SDK supports 3.8+ |
| Node | 20.x | Already set in `package.json` engines; Svelte 5 compatible |

### Tooling (Already Configured)

| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python venv + packages | `uv --version` |
| nvm | Node version management | `nvm --version` |
| npm | Node packages | `npm --version` |

### Existing Setup Commands
```bash
# Python (already configured)
source .venv/bin/activate
uv pip install -r requirements.txt

# Node (already configured)
nvm use
npm install
```

---

## 1. Anthropic Python SDK (NEW)

**Version Constraint:** `anthropic>=0.40.0`

### Installation
```bash
uv pip install anthropic
```

### Async Client (Recommended for FastAPI)

```python
import os
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # Default, can be omitted
)

async def generate_response(prompt: str) -> str:
    message = await client.messages.create(
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="claude-sonnet-4-20250514",
    )
    return message.content[0].text
```

### Sync Client (For Scripts/Testing)

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-sonnet-4-20250514",
)
print(message.content[0].text)
```

### Error Handling

```python
import anthropic
from anthropic import Anthropic

client = Anthropic()

try:
    response = client.messages.create(...)
except anthropic.APIConnectionError as e:
    # Network error - server unreachable
    print("Connection failed:", e.__cause__)
except anthropic.RateLimitError as e:
    # 429 - rate limited
    print("Rate limited, retry later")
except anthropic.APIStatusError as e:
    # Other API errors (400, 401, 500, etc.)
    print(f"API error {e.status_code}: {e.response}")
```

### Response Structure

```python
# message.content is a list of content blocks
message = await client.messages.create(...)

# For text responses:
text = message.content[0].text

# Full response object:
# message.id           - unique message ID
# message.type         - "message"
# message.role         - "assistant"
# message.content      - list of content blocks
# message.model        - model used
# message.stop_reason  - "end_turn", "max_tokens", etc.
# message.usage        - input_tokens, output_tokens
```

### Model Selection

| Model | Use Case | Cost |
|-------|----------|------|
| `claude-sonnet-4-20250514` | Best balance of speed/quality | Medium |
| `claude-opus-4-20250514` | Complex reasoning | High |
| `claude-haiku-3-5-20241022` | Fast, simple tasks | Low |

**Recommendation:** Use `claude-sonnet-4-20250514` for resume generation.

---

## 2. python-dotenv (NEW)

**Version Constraint:** `python-dotenv>=1.0.0`

### Basic Usage

```python
from dotenv import load_dotenv
import os

# Load .env file at app startup
load_dotenv()

# Access variables
api_key = os.getenv("ANTHROPIC_API_KEY")
debug = os.getenv("DEBUG", "False").lower() == "true"
```

### .env File Format

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
DEBUG=False
```

### FastAPI Integration

```python
# main.py
from dotenv import load_dotenv

# Load before any other imports that need env vars
load_dotenv()

from fastapi import FastAPI
# ... rest of app
```

### Avoid

- Don't commit `.env` to git (add to `.gitignore`)
- Don't use `override=True` unless intentional

---

## 3. FastAPI (Existing - Reference)

**Version Constraint:** `fastapi>=0.100.0` (already in requirements.txt)

### Async Endpoints (For LLM Calls)

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/resumes/generate")
async def generate_resume(job_description: str):
    # Async operations work naturally
    result = await some_async_function()
    return {"result": result}
```

### Background Tasks (Optional - For Long Operations)

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message)

@app.post("/api/resumes/generate")
async def generate_resume(
    job_description: str,
    background_tasks: BackgroundTasks
):
    result = await generate(job_description)
    background_tasks.add_task(write_log, f"Generated resume: {result.id}")
    return result
```

### Streaming Response (Optional - For Progress Updates)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def generate_stream():
    yield b'{"status": "analyzing"}\n'
    # ... do work
    yield b'{"status": "generating"}\n'
    # ... more work
    yield b'{"status": "complete", "data": {...}}\n'

@app.post("/api/resumes/generate/stream")
async def generate_resume_stream():
    return StreamingResponse(
        generate_stream(),
        media_type="application/x-ndjson"
    )
```

---

## 4. Pydantic (Existing - Reference)

**Version Constraint:** `pydantic>=2.0` (already in requirements.txt)

### Correct Patterns (v2)

```python
from pydantic import BaseModel, ConfigDict, field_validator

class ResumeRequest(BaseModel):
    job_description: str

    @field_validator("job_description")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v) < 100:
            raise ValueError("Job description must be at least 100 characters")
        return v

class GeneratedResume(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str | None
    match_score: float
    resume_content: dict
```

### Deprecated (Avoid)

| Old (v1) | New (v2) |
|----------|----------|
| `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `.from_orm(obj)` | `.model_validate(obj)` |
| `.dict()` | `.model_dump()` |
| `@validator` | `@field_validator` |

---

## 5. Svelte 5 Runes (Existing - Reference)

**Version Constraint:** `svelte>=5.0.0` (already in package.json)

### $state - Reactive State

```svelte
<script>
    // Declare reactive state
    let count = $state(0);
    let items = $state([]);
    let user = $state({ name: '', email: '' });

    // Update directly
    function increment() {
        count++;  // Triggers re-render
    }

    // Object mutation is reactive
    function updateName(name) {
        user.name = name;  // Triggers re-render
    }
</script>
```

### $effect - Side Effects

```svelte
<script>
    let count = $state(0);

    // Runs when dependencies change
    $effect(() => {
        console.log('Count changed:', count);
    });

    // Cleanup pattern
    $effect(() => {
        const timer = setInterval(() => count++, 1000);
        return () => clearInterval(timer);  // Cleanup
    });
</script>
```

### $props - Component Props

```svelte
<script>
    // Destructure props with defaults
    let {
        title,
        onSubmit,
        loading = false
    } = $props();
</script>
```

### $derived - Computed Values

```svelte
<script>
    let items = $state([]);

    // Automatically updates when items changes
    let count = $derived(items.length);
    let hasItems = $derived(items.length > 0);
</script>
```

### Async Data Loading Pattern

```svelte
<script>
    let data = $state(null);
    let loading = $state(false);
    let error = $state(null);

    async function fetchData() {
        loading = true;
        error = null;
        try {
            const res = await fetch('/api/data');
            if (!res.ok) throw new Error('Failed to fetch');
            data = await res.json();
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    // Fetch on mount
    $effect(() => {
        fetchData();
    });
</script>

{#if loading}
    <p>Loading...</p>
{:else if error}
    <p class="error">{error}</p>
{:else if data}
    <div>{JSON.stringify(data)}</div>
{/if}
```

---

## 6. SQLite (Existing - Reference)

**No additional dependencies** - uses built-in `sqlite3` module.

### Pattern from Feature 1

```python
import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "mycv.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS ...
        """)
        conn.commit()
```

---

## Dependencies Summary

**ADD TO requirements.txt:**

```
# Existing
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
pytest>=8.0.0
httpx>=0.27.0

# New for Feature 3
anthropic>=0.40.0
python-dotenv>=1.0.0
```

**No changes to package.json** - frontend dependencies unchanged.

---

## Environment Setup

**ADD TO .env (create if not exists):**

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**ADD TO .gitignore:**

```
.env
```

---

## Key Implementation Notes

1. **Anthropic client should be initialized once** at app startup, not per-request
2. **Use AsyncAnthropic** for FastAPI async endpoints
3. **Load dotenv before importing modules** that need env vars
4. **Model choice:** `claude-sonnet-4-20250514` balances cost/quality
5. **Error handling:** Wrap all Anthropic calls in try/except
6. **Token limits:** Set reasonable `max_tokens` (4096 for resume generation)

---

*Reference for /v3-design and /v3-checklist*
