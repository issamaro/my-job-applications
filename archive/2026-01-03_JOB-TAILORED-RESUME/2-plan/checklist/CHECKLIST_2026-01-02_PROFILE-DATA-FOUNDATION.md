# Checklist: Profile Data Foundation

**Date:** 2026-01-02
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

From LIBRARY_NOTES Section 0:

| Requirement | Version | Verify Command | Status |
|-------------|---------|----------------|--------|
| Python | 3.13 | `python --version` | [ ] |
| Node.js | 20 LTS | `node --version` | [ ] |
| uv | any | `uv --version` | [ ] |
| nvm | any | `nvm --version` | [ ] |

### Python Setup
- [ ] Python 3.13 installed via uv (`uv python install 3.13`)
- [ ] Python version pinned (`uv python pin 3.13`)
- [ ] Virtual environment created (`uv venv --python 3.13`)
- [ ] Virtual environment activated (`source .venv/bin/activate`)
- [ ] `.python-version` file exists with `3.13`

### Node Setup
- [ ] Node 20 installed via nvm (`nvm install 20`)
- [ ] Node 20 active (`nvm use 20`)
- [ ] `.nvmrc` file exists with `20`

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

From LIBRARY_NOTES - exact version constraints:

### Python (requirements.txt)

| Library | Constraint | Status |
|---------|-----------|--------|
| fastapi | `>=0.100.0` | [ ] |
| pydantic | `>=2.0` | [ ] |
| uvicorn | `>=0.32.0` | [ ] |

### Node (package.json devDependencies)

| Library | Constraint | Status |
|---------|-----------|--------|
| svelte | `^5.0.0` | [ ] |
| rollup | `^4.0.0` | [ ] |
| rollup-plugin-svelte | `^7.2.0` | [ ] |
| @rollup/plugin-node-resolve | `^15.0.0` | [ ] |
| @rollup/plugin-commonjs | `^25.0.0` | [ ] |
| @rollup/plugin-terser | `^0.4.0` | [ ] |
| rollup-plugin-css-only | `^4.5.0` | [ ] |
| sass | `^1.80.0` | [ ] |

**STOP if any dependency is missing or has wrong version constraint.**

---

## 2. Syntax Points

From LIBRARY_NOTES - use correct patterns:

### Pydantic v2 (NOT v1)
- [ ] Uses `model_config = ConfigDict(from_attributes=True)` → `schemas.py`
- [ ] Uses `.model_validate()` not `.from_orm()` → all route files
- [ ] Uses `.model_dump()` not `.dict()` → all route files
- [ ] Uses `str | None = None` not `Optional[str]` → `schemas.py`
- [ ] Uses `Field(default=...)` for defaults with metadata → `schemas.py`

### FastAPI
- [ ] Uses `async def` for route handlers → all route files
- [ ] Uses `response_model=` in decorators → all route files
- [ ] Uses `HTTPException` for errors → all route files

### SQLite
- [ ] Uses `sqlite3.Row` for dict-like access → `database.py`
- [ ] Uses context manager for connections → `database.py`
- [ ] Uses parameterized queries `(?, ?)` not f-strings → all route files

### Svelte 5 (NOT Svelte 4)
- [ ] Uses `$state()` for reactive state → all `.svelte` files
- [ ] Uses `$derived()` for computed values → all `.svelte` files
- [ ] Uses `$effect()` for side effects → all `.svelte` files
- [ ] Uses `onclick={}` not `on:click={}` → all `.svelte` files
- [ ] Uses `bind:value={}` for two-way binding → all `.svelte` files

### Rollup 4
- [ ] Uses `rollup-plugin-svelte` with `compilerOptions.dev` → `rollup.config.js`
- [ ] Uses `rollup-plugin-css-only` for CSS extraction → `rollup.config.js`

---

## 3. UX Points

From UX_DESIGN - implement exactly:

### Empty States
- [ ] Work Experience: "No work experience added yet." → `WorkExperience.svelte`
- [ ] Education: "No education added yet." → `Education.svelte`
- [ ] Skills: "No skills added yet." → `Skills.svelte`
- [ ] Projects: "No projects added yet." → `Projects.svelte`

### Success State
- [ ] Shows "Saved" text (not toast/modal) → all section components
- [ ] "Saved" fades after 2 seconds → CSS animation
- [ ] Green color `#008800` for saved text → `main.scss`

### Loading State
- [ ] Initial load: skeleton lines → `App.svelte`
- [ ] Save action: button shows "Saving..." → all forms
- [ ] No spinners, no progress bars → verify absence

### Error States
- [ ] Field-level: red border + message below field → all forms
- [ ] Form-level: message at top of form → all forms
- [ ] Error color `#cc0000` → `main.scss`

### Error Messages (exact text)
- [ ] Required field: "Required" → all forms
- [ ] Invalid email: "Invalid email address" → `PersonalInfo.svelte`
- [ ] Invalid date: "Invalid date" → `WorkExperience.svelte`
- [ ] End before start: "End date must be after start date" → `WorkExperience.svelte`
- [ ] Save failed: "Could not save. Please try again." → all forms
- [ ] Load failed: "Could not load profile. Please refresh." → `App.svelte`

### Layout
- [ ] Single page, vertical scroll → `App.svelte`
- [ ] No sidebar, no tabs → verify absence
- [ ] Section header with [+ Add] and [▼] buttons → `Section.svelte`

### Interaction
- [ ] Personal Info: auto-save on blur (no Save button) → `PersonalInfo.svelte`
- [ ] Other sections: explicit Save button → all other forms
- [ ] Forms expand inline (no modals) → verify absence of modals
- [ ] Delete is text link, not button → all forms
- [ ] Delete shows confirmation dialog → `ConfirmDialog.svelte`
- [ ] Sections collapsible via header click → `Section.svelte`
- [ ] All sections expanded by default → `App.svelte`

### Skills Specific
- [ ] Text input with comma parsing → `Skills.svelte`
- [ ] Creates tags from comma-separated input → `Skills.svelte`
- [ ] Tags have × button to remove → `Skills.svelte`

### Visual Design
- [ ] Font: system font stack `-apple-system, BlinkMacSystemFont...` → `main.scss`
- [ ] Body text: 16px → `main.scss`
- [ ] Headings: 20px → `main.scss`
- [ ] Text color: `#1a1a1a` → `main.scss`
- [ ] Background: `#ffffff` → `main.scss`
- [ ] Borders: `#e0e0e0` → `main.scss`
- [ ] Primary action: `#0066cc` → `main.scss`
- [ ] 16px grid spacing → `main.scss`
- [ ] 24px between sections → `main.scss`
- [ ] 12px between form fields → `main.scss`
- [ ] No shadows → verify absence
- [ ] No/minimal rounded corners (2px max) → `main.scss`
- [ ] No gradients → verify absence
- [ ] No icons (except × on tags) → verify absence

---

## 4. Test Points

From FEATURE_SPEC BDD scenarios:

### Personal Info Tests
- [ ] Test create personal info (happy path) → `tests/test_personal_info.py`
- [ ] Test update personal info → `tests/test_personal_info.py`
- [ ] Test validation error (empty name) → `tests/test_personal_info.py`
- [ ] Test validation error (empty email) → `tests/test_personal_info.py`

### Work Experience Tests
- [ ] Test add first work experience → `tests/test_work_experiences.py`
- [ ] Test add multiple work experiences → `tests/test_work_experiences.py`
- [ ] Test edit work experience → `tests/test_work_experiences.py`
- [ ] Test delete work experience → `tests/test_work_experiences.py`
- [ ] Test mark current position (end_date null) → `tests/test_work_experiences.py`
- [ ] Test chronological ordering (newest first) → `tests/test_work_experiences.py`

### Education Tests
- [ ] Test add education → `tests/test_education.py`
- [ ] Test edit education → `tests/test_education.py`
- [ ] Test delete education → `tests/test_education.py`

### Skills Tests
- [ ] Test add skills (comma parsing) → `tests/test_skills.py`
- [ ] Test remove skill → `tests/test_skills.py`
- [ ] Test duplicate skill handling → `tests/test_skills.py`

### Projects Tests
- [ ] Test add project → `tests/test_projects.py`
- [ ] Test edit project → `tests/test_projects.py`
- [ ] Test delete project → `tests/test_projects.py`

### Edge Case Tests
- [ ] Test long text in description (2000 chars) → `tests/test_validation.py`
- [ ] Test special characters (quotes, unicode) → `tests/test_validation.py`
- [ ] Test required field validation → `tests/test_validation.py`
- [ ] Test date format validation (YYYY-MM) → `tests/test_validation.py`

---

## 5. Accessibility Points

From UX_DESIGN:

- [ ] All form fields have visible labels (not placeholder-only) → all forms
- [ ] Required fields marked with `*` and `aria-required="true"` → all forms
- [ ] Error messages linked with `aria-describedby` → all forms
- [ ] Focus visible: 2px blue outline on interactive elements → `main.scss`
- [ ] Delete confirmation is dialog with focus trap → `ConfirmDialog.svelte`
- [ ] Color contrast WCAG AA (4.5:1+) for all text → verify colors
- [ ] Keyboard: Tab through fields → all forms
- [ ] Keyboard: Enter to submit forms → all forms
- [ ] Keyboard: Escape to cancel/close → all forms, `ConfirmDialog.svelte`

---

## 6. API Endpoint Verification

From IMPL_PLAN:

### Personal Info
- [ ] GET `/api/personal-info` returns PersonalInfo or empty → `routes/personal_info.py`
- [ ] PUT `/api/personal-info` creates/updates and returns PersonalInfo → `routes/personal_info.py`

### Work Experiences
- [ ] GET `/api/work-experiences` returns list (ordered) → `routes/work_experiences.py`
- [ ] POST `/api/work-experiences` creates and returns WorkExperience → `routes/work_experiences.py`
- [ ] GET `/api/work-experiences/{id}` returns single or 404 → `routes/work_experiences.py`
- [ ] PUT `/api/work-experiences/{id}` updates and returns or 404 → `routes/work_experiences.py`
- [ ] DELETE `/api/work-experiences/{id}` deletes and returns {deleted: id} → `routes/work_experiences.py`

### Education
- [ ] GET `/api/education` returns list (ordered) → `routes/education.py`
- [ ] POST `/api/education` creates and returns Education → `routes/education.py`
- [ ] GET `/api/education/{id}` returns single or 404 → `routes/education.py`
- [ ] PUT `/api/education/{id}` updates and returns or 404 → `routes/education.py`
- [ ] DELETE `/api/education/{id}` deletes and returns {deleted: id} → `routes/education.py`

### Skills
- [ ] GET `/api/skills` returns list (alphabetical) → `routes/skills.py`
- [ ] POST `/api/skills` parses comma input, returns list[Skill] → `routes/skills.py`
- [ ] DELETE `/api/skills/{id}` deletes and returns {deleted: id} → `routes/skills.py`

### Projects
- [ ] GET `/api/projects` returns list (ordered) → `routes/projects.py`
- [ ] POST `/api/projects` creates and returns Project → `routes/projects.py`
- [ ] GET `/api/projects/{id}` returns single or 404 → `routes/projects.py`
- [ ] PUT `/api/projects/{id}` updates and returns or 404 → `routes/projects.py`
- [ ] DELETE `/api/projects/{id}` deletes and returns {deleted: id} → `routes/projects.py`

---

## 7. Browser Compatibility

From LIBRARY_NOTES:

- [ ] Safari: `<input type="month">` fallback to text with YYYY-MM pattern → `WorkExperience.svelte`
- [ ] Feature detection for month input support → `WorkExperience.svelte` or `lib/api.js`

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v3-close`.

---

*Contract for /v3-implement*
