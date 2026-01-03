# Change Log: Saved Job Descriptions

**Date:** 2026-01-03
**Feature:** Saved Job Descriptions

---

## Files Changed

### Backend - New Files

| File | Description |
|------|-------------|
| `services/job_descriptions.py` | JobDescriptionService with CRUD, version history |
| `routes/job_descriptions.py` | 8 API endpoints for JD management |

### Backend - Modified Files

| File | Changes |
|------|---------|
| `database.py` | Added PRAGMA foreign_keys, job_descriptions columns, job_description_versions table |
| `main.py` | Registered job_descriptions router |
| `schemas.py` | Added 6 Pydantic models (Create, Update, ListItem, Response, WithResumes, Version) |
| `services/resume_generator.py` | Set JD title from LLM, modified delete to only remove resume |

### Frontend - New Files

| File | Description |
|------|-------------|
| `src/components/SavedJobItem.svelte` | Individual JD card with inline title editing |
| `src/components/SavedJobsList.svelte` | Collapsible panel listing saved JDs |
| `src/styles/views/_saved-jobs.scss` | Styles for saved jobs components |

### Frontend - Modified Files

| File | Changes |
|------|---------|
| `src/components/JobDescriptionInput.svelte` | Added Save button, loaded indicator, saving state |
| `src/components/ResumeGenerator.svelte` | Integrated SavedJobsList, added load/save/clear handlers |
| `src/lib/api.js` | Added 8 API functions for JD CRUD |
| `src/styles/views/_index.scss` | Added @forward "saved-jobs" |
| `src/styles/views/_resume-generator.scss` | Added loaded-indicator, button-row styles |

### Tests - New Files

| File | Tests |
|------|-------|
| `tests/test_job_descriptions.py` | 17 tests covering CRUD, validation, cascade, versions |

---

## API Endpoints Added

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/job-descriptions | List all saved JDs |
| POST | /api/job-descriptions | Create new JD |
| GET | /api/job-descriptions/{id} | Get single JD |
| PUT | /api/job-descriptions/{id} | Update JD title/text |
| DELETE | /api/job-descriptions/{id} | Delete JD with cascade |
| GET | /api/job-descriptions/{id}/resumes | Get linked resumes |
| GET | /api/job-descriptions/{id}/versions | Get version history |
| POST | /api/job-descriptions/{id}/versions/{vid}/restore | Restore version |

---

## Database Schema Changes

### New Columns (job_descriptions)
- `title` TEXT DEFAULT 'Untitled Job'
- `company_name` TEXT
- `updated_at` TEXT
- `is_saved` INTEGER DEFAULT 1

### New Table (job_description_versions)
```sql
CREATE TABLE job_description_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_description_id INTEGER NOT NULL,
    raw_text TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
);
```

### New Column (generated_resumes)
- `jd_version_id` INTEGER

---

## Test Coverage

| Test Category | Count | Status |
|---------------|-------|--------|
| New Feature Tests | 17 | PASS |
| Existing Tests | 68 | PASS |
| Pre-existing Failures | 11 | N/A (WeasyPrint) |

---

*Change Log Complete*
