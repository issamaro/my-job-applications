# Checklist: Import JSON Profile

**Date:** 2026-01-04
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

| Requirement | Version | Verify | Status |
|-------------|---------|--------|--------|
| Python | 3.13 | `python --version` | [ ] |
| Node.js | >=20.0.0 | `node --version` | [ ] |
| uv | any | `uv --version` | [ ] |

- [ ] Virtual environment exists (`.venv/`)
- [ ] Virtual environment activated (`source .venv/bin/activate`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

| Library | Constraint | Manifest | Status |
|---------|-----------|----------|--------|
| pydantic | `>=2.0` | requirements.txt | [ ] |
| fastapi | `>=0.100.0` | requirements.txt | [ ] |
| svelte | `^5.0.0` | package.json | [ ] |

- [ ] No new dependencies required (confirmed in LIBRARY_NOTES)
- [ ] Existing dependencies already satisfy requirements

**STOP if any dependency is missing.**

---

## 2. Syntax

### Svelte 5 Runes
- [ ] Use `$state()` for reactive state → `ImportModal.svelte`
- [ ] Use `$props()` for component props → `ImportModal.svelte`
- [ ] Use `$effect()` for side effects (focus management) → `ImportModal.svelte`
- [ ] Use callback props pattern (not createEventDispatcher) → `ImportModal.svelte`
- [ ] Use `onclick` attribute (not `on:click`) → `ImportModal.svelte`

### Pydantic v2
- [ ] Use `@field_validator` (not `@validator`) → `schemas.py`
- [ ] Use `str | None` syntax (not `Optional[str]`) → `schemas.py`
- [ ] Use `model_validate()` (not `parse_obj`) → `routes/profile_import.py`

### FastAPI
- [ ] Use `APIRouter` with prefix and tags → `routes/profile_import.py`
- [ ] Follow existing PUT endpoint pattern → `routes/profile_import.py`

---

## 3. UX

### Modal States
- [ ] Initial state: Drop zone with "Drag & drop your JSON file here or click to browse" → `ImportModal.svelte`
- [ ] Validating state: Spinner with "Validating..." → `ImportModal.svelte`
- [ ] Preview state: Item counts per section + warning → `ImportModal.svelte`
- [ ] Error state: Error messages + retry drop zone → `ImportModal.svelte`
- [ ] Importing state: "Importing..." on button with spinner → `ImportModal.svelte`

### Messages (Exact Text)
- [ ] Success toast: "Profile imported successfully" → `ImportModal.svelte`
- [ ] JSON syntax error: "Invalid JSON: {specific parse error}" → `ImportModal.svelte`
- [ ] Missing section: "Missing required section: personal_info" → `ImportModal.svelte`
- [ ] Missing field: "Missing required field: personal_info.full_name" → `ImportModal.svelte`
- [ ] Wrong type: "Invalid type: education[0].graduation_year must be a number" → `ImportModal.svelte`
- [ ] Server error: "Import failed. Please try again." → `ImportModal.svelte`
- [ ] File read error: "Could not read file. Please try again." → `ImportModal.svelte`

### Warnings
- [ ] Data replacement warning: "This will replace all existing data." → `ImportModal.svelte`
- [ ] Photo preservation note: "Your profile photo will be preserved." → `ImportModal.svelte`

### Actions
- [ ] "Download Sample JSON" link visible in initial and error states → `ImportModal.svelte`
- [ ] "Cancel" button closes modal → `ImportModal.svelte`
- [ ] "Import" button triggers import → `ImportModal.svelte`
- [ ] Modal closes on: X button, Cancel, Escape key, backdrop click, successful import → `ImportModal.svelte`

---

## 4. Tests

### Backend Tests (`tests/test_profile_import.py`)
- [ ] Happy path: Valid JSON imports all sections
- [ ] Preserves photo: Existing photo not cleared after import
- [ ] Missing personal_info: Returns 422 with clear error
- [ ] Missing required field: Returns 422 with field path
- [ ] Invalid date format: Returns 422 for wrong YYYY-MM
- [ ] Invalid email: Returns 422 for malformed email
- [ ] Empty arrays: Clears existing data for those sections
- [ ] Atomicity: Partial failure rolls back entire import

### Frontend Validation (Manual Testing)
- [ ] Invalid JSON syntax shows parse error
- [ ] Missing section shows specific error
- [ ] Missing required field shows field path
- [ ] Wrong type shows type error
- [ ] Multiple errors show first 5 only

---

## 5. Accessibility

### Keyboard Navigation
- [ ] Tab navigates through all interactive elements in modal → `ImportModal.svelte`
- [ ] Escape key closes modal → `ImportModal.svelte`
- [ ] Enter/Space activates drop zone → `ImportModal.svelte`
- [ ] Focus trapped inside modal while open → `ImportModal.svelte`

### Focus Management
- [ ] Focus moves to modal when opened → `ImportModal.svelte`
- [ ] Focus returns to "Import JSON" button when modal closes → `ProfileEditor.svelte`
- [ ] Focus indicators visible on buttons and drop zone → `ImportModal.svelte`

### ARIA
- [ ] Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` → `ImportModal.svelte`
- [ ] Drop zone: `role="button"`, `aria-label` → `ImportModal.svelte`
- [ ] Loading state: `aria-busy="true"` → `ImportModal.svelte`
- [ ] Error messages: `aria-live="assertive"` → `ImportModal.svelte`
- [ ] Success toast: `role="status"`, `aria-live="polite"` → `Toast.svelte` (existing)

### Screen Reader
- [ ] Modal title announced → `ImportModal.svelte`
- [ ] Validation errors announced → `ImportModal.svelte`
- [ ] Import success announced → `Toast.svelte`

---

## 6. Project-Specific

None - no project-checks.md found

---

## 7. Implementation Files Checklist

### Backend
- [ ] `schemas.py` - Import schemas added (PersonalInfoImport, WorkExperienceImport, EducationImport, SkillImport, ProjectImport, ProfileImport)
- [ ] `routes/profile_import.py` - Created with PUT `/api/profile/import`
- [ ] `main.py` - Router registered

### Frontend
- [ ] `src/lib/api.js` - `importProfile()` function added
- [ ] `public/sample-profile.json` - Sample JSON created
- [ ] `src/components/ImportModal.svelte` - Full modal component
- [ ] `src/components/ProfileEditor.svelte` - "Import JSON" button added

### Tests
- [ ] `tests/test_profile_import.py` - All test cases

---

## 8. Sample JSON Checklist

The `public/sample-profile.json` must include:
- [ ] `personal_info` with all fields (full_name, email, phone, location, linkedin_url, summary)
- [ ] `work_experiences` array with example item (company, title, start_date, end_date, is_current, description, location)
- [ ] `education` array with example item (institution, degree, field_of_study, graduation_year, gpa, notes)
- [ ] `skills` array with example items ({ name: "..." })
- [ ] `projects` array with example item (name, description, technologies, url, start_date, end_date)
- [ ] Realistic placeholder values showing expected format
- [ ] Valid JSON syntax (no trailing commas)

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v4-close`.

---

*Contract for /v4-implement*
