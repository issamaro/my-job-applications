# Change Log: Profile Data Foundation

**Date:** 2026-01-02
**Feature:** Profile Data Foundation - CV profile management with 5 CRUD sections

---

## Summary

Initial implementation of MyCV application - a CV/resume profile editor with FastAPI backend and Svelte 5 frontend.

---

## Files Created

### Configuration (6 files)

| File | Purpose |
|------|---------|
| `.python-version` | Pin Python 3.13 |
| `.nvmrc` | Pin Node 20 |
| `.npmrc` | Enable engine-strict for Node version enforcement |
| `requirements.txt` | Python dependencies (fastapi, pydantic, uvicorn, pytest, httpx) |
| `package.json` | Node dependencies (svelte 5, rollup 4, sass) |
| `rollup.config.js` | Svelte/Rollup build configuration |

### Backend (9 files)

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 24 | FastAPI app with lifespan, router includes, static mount |
| `database.py` | 68 | SQLite connection manager, init_db() with schema |
| `schemas.py` | 147 | Pydantic v2 models for all entities |
| `routes/__init__.py` | 0 | Package marker |
| `routes/personal_info.py` | 54 | GET/PUT for single-row personal_info |
| `routes/work_experiences.py` | 96 | Full CRUD for work_experiences |
| `routes/education.py` | 89 | Full CRUD for education |
| `routes/skills.py` | 52 | GET all, POST (comma parse), DELETE |
| `routes/projects.py` | 88 | Full CRUD for projects |

### Frontend (13 files)

| File | Lines | Purpose |
|------|-------|---------|
| `public/index.html` | 12 | HTML shell loading bundle.js and CSS |
| `src/main.js` | 8 | Svelte 5 app mount point |
| `src/App.svelte` | 32 | Main component composing 5 sections |
| `src/lib/api.js` | 119 | Fetch wrapper for all API calls |
| `src/styles/main.scss` | 414 | Global styles per UX_DESIGN |
| `src/components/Section.svelte` | 37 | Collapsible section wrapper with a11y |
| `src/components/ConfirmDialog.svelte` | 42 | Delete confirmation dialog |
| `src/components/PersonalInfo.svelte` | 126 | Auto-save form for personal info |
| `src/components/WorkExperience.svelte` | 350 | List + inline form with date validation |
| `src/components/Education.svelte` | 260 | List + inline form |
| `src/components/Skills.svelte` | 100 | Tag input with comma parsing |
| `src/components/Projects.svelte` | 230 | List + inline form |

### Tests (8 files)

| File | Tests | Purpose |
|------|-------|---------|
| `tests/__init__.py` | - | Package marker |
| `tests/conftest.py` | - | Pytest fixtures, temp DB setup |
| `tests/test_personal_info.py` | 6 | CRUD + validation tests |
| `tests/test_work_experiences.py` | 8 | CRUD + ordering tests |
| `tests/test_education.py` | 5 | CRUD tests |
| `tests/test_skills.py` | 6 | CRUD + comma parsing tests |
| `tests/test_projects.py` | 5 | CRUD tests |
| `tests/test_validation.py` | 5 | Edge case validation tests |

### Generated (build output)

| File | Purpose |
|------|---------|
| `public/build/bundle.js` | Compiled Svelte app |
| `public/build/bundle.css` | Extracted component styles |
| `public/build/global.css` | Compiled Sass |

---

## Database Schema

5 tables created in `app.db`:

1. **personal_info** - Single-row with CHECK(id=1)
2. **work_experiences** - With is_current flag, ordered by start_date DESC
3. **education** - With graduation_year, ordered DESC
4. **skills** - Simple name list, UNIQUE constraint, ordered alphabetically
5. **projects** - With technologies field, ordered by created_at DESC

---

## API Endpoints

| Endpoint | Methods | Notes |
|----------|---------|-------|
| `/api/personal-info` | GET, PUT | Single resource (upsert) |
| `/api/work-experiences` | GET, POST | Collection |
| `/api/work-experiences/{id}` | GET, PUT, DELETE | Single resource |
| `/api/education` | GET, POST | Collection |
| `/api/education/{id}` | GET, PUT, DELETE | Single resource |
| `/api/skills` | GET, POST | POST parses comma input |
| `/api/skills/{id}` | DELETE | Single resource |
| `/api/projects` | GET, POST | Collection |
| `/api/projects/{id}` | GET, PUT, DELETE | Single resource |

---

## Test Results

- **35 tests passed**
- **0 failures**
- All BDD scenarios covered

---

## Dependencies Installed

### Python (in .venv)
- fastapi 0.128.0
- pydantic 2.12.5
- uvicorn 0.40.0
- pytest 9.0.2
- httpx 0.28.1

### Node (in node_modules)
- svelte 5.46.1
- rollup 4.54.0
- sass 1.97.1

---

*Change log for /v3-close*
