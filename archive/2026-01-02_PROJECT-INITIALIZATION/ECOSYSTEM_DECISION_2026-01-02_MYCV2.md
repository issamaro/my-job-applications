# Ecosystem Decision: MyCV-2

**Date:** 2026-01-02 (Retrofitted: 2026-01-04)
**Project:** AI-Powered Resume Management System
**Status:** DECIDED

---

## Project Vision

A single-user web application for creating job-tailored resumes with AI-powered analysis. Users enter their professional experience once, then generate customized resumes on-demand for each job application.

---

## Technology Decisions

### Backend Stack

| Technology | Version | Rationale |
|------------|---------|-----------|
| **Python** | 3.13+ | Highest stable with full library support (FastAPI, Pydantic, Uvicorn) |
| **FastAPI** | >=0.100.0 | Modern async framework, automatic OpenAPI docs, Pydantic integration |
| **Pydantic** | >=2.0 | Type-safe validation, v2 syntax (model_validate, model_dump) |
| **Uvicorn** | >=0.32.0 | ASGI server, v0.32+ officially supports Python 3.13 |
| **SQLite** | stdlib | Single-user, no external DB needed, file-based persistence |
| **Anthropic SDK** | >=0.40.0 | Claude API for resume generation |
| **WeasyPrint** | >=62.0 | HTML/CSS to PDF conversion |
| **Jinja2** | >=3.1.0 | PDF template rendering |

### Frontend Stack

| Technology | Version | Rationale |
|------------|---------|-----------|
| **Svelte** | ^5.0.0 | Modern runes syntax ($state, $derived, $effect), no virtual DOM |
| **Rollup** | ^4.0.0 | Simple bundler, native ESM, Svelte official support |
| **Sass** | ^1.80.0 | SCSS with design tokens system |
| **Node.js** | 20 LTS | Svelte 5 and Rollup require modern Node |

### Tooling

| Tool | Purpose |
|------|---------|
| `uv` | Python version + venv + package management |
| `nvm` | Node version management |
| `pytest` | Python testing with async support |
| `.nvmrc` + `.python-version` | Version pinning |

---

## Architecture Decisions

### 1. No ORM
- **Decision:** Use raw sqlite3 with parameterized queries
- **Rationale:** 8 tables, single user, simpler than SQLAlchemy overhead
- **Trade-off:** Manual schema management, but full control

### 2. Layered Backend
- **Routes** (`routes/*.py`): HTTP endpoints, validation
- **Services** (`services/*.py`): Business logic, LLM integration
- **Database** (`database.py`): SQLite schema, connection management
- **Schemas** (`schemas.py`): Pydantic models

### 3. Component-Driven Frontend
- **Components** (`src/components/`): Reusable Svelte components
- **Styles** (`src/styles/`): Modular SCSS with design tokens
- **API Client** (`src/lib/api.js`): Fetch wrapper

### 4. No SvelteKit
- **Decision:** Plain Svelte 5 + Rollup, served via FastAPI static files
- **Rationale:** Single-page app, no SSR needed, simpler deployment

### 5. Environment-Based Config
- `.env` for secrets (ANTHROPIC_API_KEY)
- `.env.example` as template
- No committed secrets

---

## System Dependencies (macOS)

```bash
# WeasyPrint requires Pango/Cairo
brew install pango

# Library path for WeasyPrint
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
```

---

## Validation Checks

The project uses the following checks to verify foundation health:

### 1. Backend Health
```bash
# Activate venv
source venv/bin/activate

# Test FastAPI imports
python -c "from main import app; print('OK')"

# Run test suite
python -m pytest -v
```

### 2. Frontend Health
```bash
# Build SCSS + Rollup bundle
npm run build

# Verify output exists
ls public/build/bundle.js public/build/global.css
```

### 3. Development Server
```bash
# Start full stack (backend + frontend watch)
./dev.sh
# → http://localhost:8000
# → Swagger: http://localhost:8000/docs
```

---

## Lessons from Retrospectives

Extracted from archived feature retrospectives:

1. **Ecosystem Setup**: `uv` for Python + `.nvmrc` for Node provides reliable version pinning
2. **Library Research**: Context7 lookups for syntax patterns prevent deprecated code
3. **Lazy Imports**: Heavy libraries (WeasyPrint) should be imported inside functions
4. **Test Isolation**: Use temp files for SQLite, not `:memory:` (each connection is fresh)
5. **Prompt Engineering**: LLM work deserves dedicated iteration time

---

## Directory Structure

```
MyCV-2/
├── src/                    # Frontend (Svelte 5)
├── routes/                 # FastAPI routers
├── services/               # Business logic
├── templates/              # Jinja2 PDF templates
├── tests/                  # pytest suite
├── public/                 # Static files (build output)
├── workbench/              # Active development
├── backlog/                # Feature queue
├── archive/                # Completed features
├── main.py                 # FastAPI app
├── database.py             # SQLite setup
├── schemas.py              # Pydantic models
├── requirements.txt        # Python deps
├── package.json            # Node deps
├── rollup.config.js        # Bundler config
└── dev.sh                  # Dev server launcher
```

---

*Ecosystem Decision documented for v4 methodology compliance*
