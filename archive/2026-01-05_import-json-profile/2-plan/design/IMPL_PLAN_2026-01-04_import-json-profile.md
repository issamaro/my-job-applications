# Implementation Plan: Import JSON Profile

**Date:** 2026-01-04
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-04_import-json-profile.md

---

## 1. Affected Files

### Config/Dependencies
| File | Change | Description |
|------|--------|-------------|
| None | - | No new dependencies required (LIBRARY_NOTES confirms all versions compatible) |

### Backend
| File | Change | Description |
|------|--------|-------------|
| `schemas.py` | Modify | Add `ProfileImport` and nested import schemas for validation |
| `routes/profile_import.py` | Create | New router for `/api/profile/import` endpoint |
| `main.py` | Modify | Register the new `profile_import` router |

### Frontend
| File | Change | Description |
|------|--------|-------------|
| `src/components/ImportModal.svelte` | Create | Modal component with file upload, validation, preview, and import |
| `src/components/ProfileEditor.svelte` | Modify | Add "Import JSON" button to trigger modal |
| `src/lib/api.js` | Modify | Add `importProfile()` function |
| `public/sample-profile.json` | Create | Sample JSON file for download |

### Tests
| File | Change | Description |
|------|--------|-------------|
| `tests/test_profile_import.py` | Create | Tests for import endpoint (happy path, validation errors, atomicity) |

---

## 2. Database Changes

```sql
-- None
-- Existing tables already support the import:
-- - personal_info (single row, id=1)
-- - work_experiences
-- - education
-- - skills
-- - projects
```

---

## 3. Implementation Approach

### Service Pattern

**No separate service layer** - Follow existing project pattern where routes directly interact with database. The import operation is straightforward: clear existing data and insert new data within a single transaction.

### Validation Strategy

**Two-Layer Validation:**

1. **Frontend (first line):**
   - JSON syntax validation (try/catch on JSON.parse)
   - Schema structure validation (required sections exist)
   - Required field validation (full_name, email, company, title, etc.)
   - Type validation (graduation_year is number, etc.)
   - Show all errors at once (up to 5), not one at a time

2. **Backend (second line):**
   - Pydantic model validation (type coercion, field validators)
   - Same validations as existing schemas (date format YYYY-MM, email format)
   - Returns 422 with detailed errors if validation fails

### Import Algorithm (Backend)

```python
# Atomic operation within single transaction:
with get_db() as conn:
    # 1. Clear existing data (except photo)
    conn.execute("DELETE FROM work_experiences")
    conn.execute("DELETE FROM education")
    conn.execute("DELETE FROM skills")
    conn.execute("DELETE FROM projects")

    # 2. Update personal_info (preserve photo column)
    conn.execute("""
        UPDATE personal_info SET
            full_name=?, email=?, phone=?, location=?,
            linkedin_url=?, summary=?, updated_at=CURRENT_TIMESTAMP
        WHERE id = 1
    """)
    # Or INSERT if not exists

    # 3. Insert new data
    for exp in profile.work_experiences:
        conn.execute("INSERT INTO work_experiences ...")
    # ... same for education, skills, projects

    # 4. Commit (all or nothing)
    conn.commit()
```

### Error Handling

| Layer | Error Type | Response |
|-------|------------|----------|
| Frontend | JSON parse error | Show "Invalid JSON: {message}" |
| Frontend | Missing section | Show "Missing required section: {name}" |
| Frontend | Missing field | Show "Missing required field: {path}" |
| Frontend | Wrong type | Show "Invalid type: {path} must be {type}" |
| Backend | Pydantic validation | 422 with detail array |
| Backend | Database error | 500 with "Import failed. Please try again." |

### Post-Import Refresh

**Strategy:** Page reload after successful import
- Simplest approach for MVP
- Ensures all components reload fresh data
- Toast message shows before reload

---

## 4. Implementation Order

### Phase 1: Backend (Routes + Schemas)
1. [ ] `schemas.py` - Add import schemas (`PersonalInfoImport`, `WorkExperienceImport`, `EducationImport`, `SkillImport`, `ProjectImport`, `ProfileImport`)
2. [ ] `routes/profile_import.py` - Create PUT `/api/profile/import` endpoint with atomic clear+insert
3. [ ] `main.py` - Register `profile_import.router`

### Phase 2: Frontend (Modal + Integration)
4. [ ] `src/lib/api.js` - Add `importProfile(data)` function
5. [ ] `public/sample-profile.json` - Create sample JSON file
6. [ ] `src/components/ImportModal.svelte` - Create modal with all states (initial, validating, preview, error, importing)
7. [ ] `src/components/ProfileEditor.svelte` - Add "Import JSON" button and modal integration

### Phase 3: Tests
8. [ ] `tests/test_profile_import.py` - Write tests for import endpoint

---

## 5. Detailed Component Design

### Backend Schemas (`schemas.py`)

```python
# Import-specific schemas (no id, no timestamps)
class PersonalInfoImport(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    summary: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email address")
        return v

class WorkExperienceImport(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    location: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Invalid date format. Use YYYY-MM")
        return v

class EducationImport(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    graduation_year: int | None = None
    gpa: float | None = None
    notes: str | None = None

    @field_validator("graduation_year")
    @classmethod
    def validate_graduation_year(cls, v: int | None) -> int | None:
        if v is not None and (v < 1900 or v > 2100):
            raise ValueError("Graduation year must be between 1900 and 2100")
        return v

class SkillImport(BaseModel):
    name: str

class ProjectImport(BaseModel):
    name: str
    description: str | None = None
    technologies: str | None = None
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Invalid date format. Use YYYY-MM")
        return v

class ProfileImport(BaseModel):
    personal_info: PersonalInfoImport
    work_experiences: list[WorkExperienceImport] = []
    education: list[EducationImport] = []
    skills: list[SkillImport] = []
    projects: list[ProjectImport] = []
```

### Frontend Validation (`ImportModal.svelte`)

```javascript
function validateProfileJson(data) {
  const errors = [];

  // Required sections
  if (!data.personal_info) {
    errors.push('Missing required section: personal_info');
  }

  // Required fields in personal_info
  if (data.personal_info) {
    if (!data.personal_info.full_name) {
      errors.push('Missing required field: personal_info.full_name');
    }
    if (!data.personal_info.email) {
      errors.push('Missing required field: personal_info.email');
    }
  }

  // Array sections should be arrays
  ['work_experiences', 'education', 'skills', 'projects'].forEach(section => {
    if (data[section] !== undefined && !Array.isArray(data[section])) {
      errors.push(`${section} must be an array`);
    }
  });

  // Required fields in array items
  if (Array.isArray(data.work_experiences)) {
    data.work_experiences.forEach((item, i) => {
      if (!item.company) errors.push(`Missing required field: work_experiences[${i}].company`);
      if (!item.title) errors.push(`Missing required field: work_experiences[${i}].title`);
      if (!item.start_date) errors.push(`Missing required field: work_experiences[${i}].start_date`);
    });
  }

  // ... similar for education (institution, degree), skills (name), projects (name)

  // Type validations
  if (Array.isArray(data.education)) {
    data.education.forEach((item, i) => {
      if (item.graduation_year !== undefined && typeof item.graduation_year !== 'number') {
        errors.push(`Invalid type: education[${i}].graduation_year must be a number`);
      }
    });
  }

  return errors.slice(0, 5); // Return first 5 errors
}
```

### Modal States Flow

```
[Initial] --file selected--> [Validating] --valid--> [Preview]
                                          --invalid--> [Error]
[Preview] --confirm--> [Importing] --success--> [Close + Toast + Reload]
                                   --fail--> [Error]
[Error] --new file--> [Validating]
```

---

## 6. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Frontend validation misses edge case | Med | Low | Backend Pydantic validates as second line |
| Large JSON file causes slow parsing | Low | Low | Text-based profile data is inherently small |
| Transaction fails mid-import | Low | High | SQLite transactions are atomic; rollback automatic |
| Photo accidentally cleared | Med | High | Import endpoint explicitly preserves photo column |
| Modal state gets stuck | Low | Med | Add timeout and error boundary |

---

## 7. API Contract

### PUT `/api/profile/import`

**Request Body:**
```json
{
  "personal_info": {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1 555-1234",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/janedoe",
    "summary": "Experienced engineer..."
  },
  "work_experiences": [
    {
      "company": "Tech Corp",
      "title": "Senior Engineer",
      "start_date": "2020-01",
      "end_date": null,
      "is_current": true,
      "description": "Lead development...",
      "location": "San Francisco, CA"
    }
  ],
  "education": [
    {
      "institution": "State University",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "graduation_year": 2018,
      "gpa": 3.8,
      "notes": ""
    }
  ],
  "skills": [
    { "name": "JavaScript" },
    { "name": "Python" }
  ],
  "projects": [
    {
      "name": "Open Source Tool",
      "description": "A CLI tool for...",
      "technologies": "Node.js, TypeScript",
      "url": "https://github.com/example/tool",
      "start_date": "2022-06",
      "end_date": "2022-12"
    }
  ]
}
```

**Success Response (200):**
```json
{
  "message": "Profile imported successfully",
  "counts": {
    "work_experiences": 3,
    "education": 2,
    "skills": 8,
    "projects": 4
  }
}
```

**Validation Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "personal_info", "email"],
      "msg": "Invalid email address",
      "type": "value_error"
    }
  ]
}
```

---

*Next: /v4-checklist*
