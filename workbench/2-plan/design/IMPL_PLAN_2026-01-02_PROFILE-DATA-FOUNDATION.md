# Implementation Plan: Profile Data Foundation

**Date:** 2026-01-02
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-02_PROFILE-DATA-FOUNDATION.md

---

## 1. Affected Files

### Config/Dependencies

| File | Change | Description |
|------|--------|-------------|
| `requirements.txt` | Create | `fastapi>=0.100.0`, `pydantic>=2.0`, `uvicorn>=0.32.0` |
| `package.json` | Create | Svelte 5, Rollup 4, Sass, plugins (see LIBRARY_NOTES) |
| `rollup.config.js` | Create | Svelte + CSS extraction config |
| `.python-version` | Create | Pin Python 3.13 |
| `.nvmrc` | Create | Pin Node 20 |

### Backend

| File | Change | Description |
|------|--------|-------------|
| `main.py` | Create | FastAPI app, static file mounting, CORS, init_db call |
| `database.py` | Create | SQLite connection context manager, init_db() with schema |
| `schemas.py` | Create | Pydantic v2 models for all entities (Create/Update/Response) |
| `routes/personal_info.py` | Create | GET/PUT for single-row personal_info |
| `routes/work_experiences.py` | Create | Full CRUD for work_experiences |
| `routes/education.py` | Create | Full CRUD for education |
| `routes/skills.py` | Create | GET all, POST (with comma parsing), DELETE single |
| `routes/projects.py` | Create | Full CRUD for projects |

### Frontend

| File | Change | Description |
|------|--------|-------------|
| `public/index.html` | Create | Shell HTML that loads bundle.js |
| `src/main.js` | Create | Svelte app mount point |
| `src/App.svelte` | Create | Main component with 5 sections |
| `src/components/PersonalInfo.svelte` | Create | Form with auto-save on blur |
| `src/components/WorkExperience.svelte` | Create | List + inline add/edit form |
| `src/components/Education.svelte` | Create | List + inline add/edit form |
| `src/components/Skills.svelte` | Create | Tag input with comma parsing |
| `src/components/Projects.svelte` | Create | List + inline add/edit form |
| `src/components/Section.svelte` | Create | Collapsible section wrapper |
| `src/components/ConfirmDialog.svelte` | Create | Delete confirmation dialog |
| `src/lib/api.js` | Create | Fetch wrapper for all API calls |
| `src/styles/main.scss` | Create | Global styles per UX_DESIGN |
| `public/build/global.css` | Generated | Compiled Sass output |

### Tests

| File | Change | Description |
|------|--------|-------------|
| `tests/conftest.py` | Create | Pytest fixtures, test DB setup |
| `tests/test_personal_info.py` | Create | CRUD tests for personal_info |
| `tests/test_work_experiences.py` | Create | CRUD tests for work_experiences |
| `tests/test_education.py` | Create | CRUD tests for education |
| `tests/test_skills.py` | Create | CRUD tests for skills |
| `tests/test_projects.py` | Create | CRUD tests for projects |
| `tests/test_validation.py` | Create | Schema validation edge cases |

### Documentation

| File | Change | Description |
|------|--------|-------------|
| (none) | — | No docs required for MVP |

---

## 2. Database Changes

```sql
-- New database: app.db

-- Personal info (single row enforced)
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

-- Work experiences
CREATE TABLE IF NOT EXISTS work_experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    is_current INTEGER DEFAULT 0,
    description TEXT,
    location TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Education
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    graduation_year INTEGER,
    gpa REAL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Skills (simple name list)
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    technologies TEXT,
    url TEXT,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Implementation Approach

### Project Structure

```
MyCV-2/
├── main.py                 # FastAPI entry point
├── database.py             # SQLite helpers
├── schemas.py              # Pydantic models
├── routes/
│   ├── __init__.py
│   ├── personal_info.py
│   ├── work_experiences.py
│   ├── education.py
│   ├── skills.py
│   └── projects.py
├── public/
│   ├── index.html
│   └── build/
│       ├── bundle.js       # Rollup output
│       ├── bundle.css      # Svelte component styles
│       └── global.css      # Compiled Sass
├── src/
│   ├── main.js
│   ├── App.svelte
│   ├── components/
│   │   ├── PersonalInfo.svelte
│   │   ├── WorkExperience.svelte
│   │   ├── Education.svelte
│   │   ├── Skills.svelte
│   │   ├── Projects.svelte
│   │   ├── Section.svelte
│   │   └── ConfirmDialog.svelte
│   ├── lib/
│   │   └── api.js
│   └── styles/
│       └── main.scss
├── tests/
│   ├── conftest.py
│   ├── test_personal_info.py
│   ├── test_work_experiences.py
│   ├── test_education.py
│   ├── test_skills.py
│   └── test_projects.py
├── requirements.txt
├── package.json
├── rollup.config.js
├── .python-version
├── .nvmrc
└── app.db                  # SQLite database (created at runtime)
```

### API Design

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/personal-info` | GET | — | PersonalInfo |
| `/api/personal-info` | PUT | PersonalInfoUpdate | PersonalInfo |
| `/api/work-experiences` | GET | — | list[WorkExperience] |
| `/api/work-experiences` | POST | WorkExperienceCreate | WorkExperience |
| `/api/work-experiences/{id}` | GET | — | WorkExperience |
| `/api/work-experiences/{id}` | PUT | WorkExperienceUpdate | WorkExperience |
| `/api/work-experiences/{id}` | DELETE | — | {deleted: id} |
| `/api/education` | GET | — | list[Education] |
| `/api/education` | POST | EducationCreate | Education |
| `/api/education/{id}` | GET | — | Education |
| `/api/education/{id}` | PUT | EducationUpdate | Education |
| `/api/education/{id}` | DELETE | — | {deleted: id} |
| `/api/skills` | GET | — | list[Skill] |
| `/api/skills` | POST | SkillCreate | list[Skill] (parsed) |
| `/api/skills/{id}` | DELETE | — | {deleted: id} |
| `/api/projects` | GET | — | list[Project] |
| `/api/projects` | POST | ProjectCreate | Project |
| `/api/projects/{id}` | GET | — | Project |
| `/api/projects/{id}` | PUT | ProjectUpdate | Project |
| `/api/projects/{id}` | DELETE | — | {deleted: id} |

### Validation Approach

**Backend (Pydantic v2):**
- Required fields: `full_name`, `email` (personal_info); `company`, `title`, `start_date` (work); `institution`, `degree` (education); `name` (skills/projects)
- Date format: YYYY-MM validated via regex pattern
- End date vs start date: Custom validator (end >= start or is_current)
- Unique skill names: DB constraint + duplicate check on insert

**Frontend (Svelte):**
- Required fields: `required` attribute + red border on blur if empty
- Date inputs: `<input type="month">` with text fallback for Safari
- Inline error display below field

### Auto-save Pattern (Personal Info)

```javascript
// PersonalInfo.svelte
let saveTimeout;

function handleBlur() {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(async () => {
    await api.updatePersonalInfo(formData);
    showSavedIndicator();
  }, 500);
}
```

### List Ordering

- Work experiences: ORDER BY `is_current DESC, start_date DESC` (current first, then newest)
- Education: ORDER BY `graduation_year DESC`
- Projects: ORDER BY `created_at DESC` (most recently added)
- Skills: ORDER BY `name ASC` (alphabetical)

### Error Handling

**Backend:**
- 404: Item not found
- 422: Validation error (Pydantic returns field-level errors)
- 500: Database error (log, return generic message)

**Frontend:**
- Display field-level errors from 422 response
- Show generic error banner for 500
- Retry button for failed loads

---

## 4. Implementation Order

### Phase 1: Backend Foundation
1. [ ] `requirements.txt` — dependency versions from LIBRARY_NOTES
2. [ ] `.python-version` — pin 3.13
3. [ ] `database.py` — SQLite connection + init_db() with full schema
4. [ ] `schemas.py` — all Pydantic v2 models
5. [ ] `routes/personal_info.py` — GET/PUT endpoints
6. [ ] `routes/work_experiences.py` — full CRUD
7. [ ] `routes/education.py` — full CRUD
8. [ ] `routes/skills.py` — GET all, POST (comma parse), DELETE
9. [ ] `routes/projects.py` — full CRUD
10. [ ] `main.py` — FastAPI app, route includes, static mount

### Phase 2: Backend Tests
11. [ ] `tests/conftest.py` — fixtures, test DB
12. [ ] `tests/test_personal_info.py`
13. [ ] `tests/test_work_experiences.py`
14. [ ] `tests/test_education.py`
15. [ ] `tests/test_skills.py`
16. [ ] `tests/test_projects.py`
17. [ ] Run pytest, fix any failures

### Phase 3: Frontend Foundation
18. [ ] `package.json` — dependencies from LIBRARY_NOTES
19. [ ] `.nvmrc` — pin Node 20
20. [ ] `rollup.config.js` — Svelte 5 + CSS config
21. [ ] `public/index.html` — HTML shell
22. [ ] `src/main.js` — Svelte mount
23. [ ] `src/lib/api.js` — fetch wrapper
24. [ ] `src/styles/main.scss` — global styles per UX_DESIGN
25. [ ] npm install + build verification

### Phase 4: Frontend Components
26. [ ] `src/components/Section.svelte` — collapsible wrapper
27. [ ] `src/components/ConfirmDialog.svelte` — delete confirmation
28. [ ] `src/components/PersonalInfo.svelte` — form with auto-save
29. [ ] `src/components/WorkExperience.svelte` — list + inline form
30. [ ] `src/components/Education.svelte` — list + inline form
31. [ ] `src/components/Skills.svelte` — tag input
32. [ ] `src/components/Projects.svelte` — list + inline form
33. [ ] `src/App.svelte` — compose all sections

### Phase 5: Integration
34. [ ] Verify full CRUD flow for each section
35. [ ] Test empty states
36. [ ] Test validation errors
37. [ ] Test delete confirmations
38. [ ] Cross-browser check (Safari date input fallback)

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Safari `<input type="month">` unsupported | High | Low | Use text input with YYYY-MM pattern as fallback |
| Svelte 5 breaking changes | Low | Med | Pin exact versions, use LIBRARY_NOTES patterns |
| SQLite concurrent writes | Low | Low | Single user app; no concurrent access |
| Large descriptions truncated | Low | Low | Use TEXT type, no length limit in SQLite |

---

## 6. Decisions Made

| Decision | Rationale |
|----------|-----------|
| No ORM | Direct SQLite is simpler for 5 tables, avoids SQLAlchemy complexity |
| Single schemas.py | All models in one file; not enough entities to split |
| routes/ folder | Separate file per entity for clean organization |
| Auto-save only for PersonalInfo | Other sections have explicit Save to avoid accidental changes |
| No state persistence for collapse | Always expanded on load is fine; avoids localStorage complexity |

---

*Next: /v3-checklist*
