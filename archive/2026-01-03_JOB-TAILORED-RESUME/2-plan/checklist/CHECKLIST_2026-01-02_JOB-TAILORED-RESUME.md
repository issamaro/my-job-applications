# Checklist: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

From LIBRARY_NOTES Section 0:

| Requirement | Version | Verify Command | Status |
|-------------|---------|----------------|--------|
| Python | 3.13 | `python --version` | [ ] |
| Node | 20.x | `node --version` | [ ] |
| uv | any | `uv --version` | [ ] |
| nvm | any | `nvm --version` | [ ] |

- [ ] Virtual environment activated (`source .venv/bin/activate`)
- [ ] Node version set (`nvm use`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

From LIBRARY_NOTES - exact version constraints:

### Python (requirements.txt)

| Library | Constraint | Status |
|---------|-----------|--------|
| fastapi | `>=0.100.0` | [ ] Already present |
| pydantic | `>=2.0` | [ ] Already present |
| uvicorn | `>=0.32.0` | [ ] Already present |
| pytest | `>=8.0.0` | [ ] Already present |
| httpx | `>=0.27.0` | [ ] Already present |
| anthropic | `>=0.40.0` | [ ] **NEW** |
| python-dotenv | `>=1.0.0` | [ ] **NEW** |

### Node (package.json) - No changes needed

| Library | Constraint | Status |
|---------|-----------|--------|
| svelte | `^5.0.0` | [ ] Already present |

### Environment

| File | Content | Status |
|------|---------|--------|
| `.env` | `ANTHROPIC_API_KEY=` | [ ] Created |
| `.env.example` | Template without secrets | [ ] Created |
| `.gitignore` | Contains `.env` | [ ] Updated |

**STOP if any dependency is missing or has wrong version constraint.**

---

## 2. Syntax Points

From LIBRARY_NOTES - use correct patterns:

### Anthropic SDK
- [ ] Uses `AsyncAnthropic` client (not sync) for FastAPI
- [ ] Client initialized once at startup, not per-request
- [ ] API key loaded from `os.environ.get("ANTHROPIC_API_KEY")`
- [ ] Model: `claude-sonnet-4-20250514`
- [ ] Response accessed via `message.content[0].text`
- [ ] Error handling: catches `APIConnectionError`, `RateLimitError`, `APIStatusError`

### python-dotenv
- [ ] `load_dotenv()` called before other imports that need env vars
- [ ] Called in `main.py` at top

### Pydantic (v2)
- [ ] Uses `model_config = ConfigDict(from_attributes=True)` for ORM mode
- [ ] Uses `@field_validator` not `@validator`
- [ ] Uses `.model_dump()` not `.dict()`

### Svelte 5 Runes
- [ ] Uses `$state()` for reactive state
- [ ] Uses `$effect()` for side effects
- [ ] Uses `$props()` for component props
- [ ] Uses `$derived()` for computed values

### FastAPI Async
- [ ] All LLM-calling endpoints are `async def`
- [ ] Uses `await` for Anthropic calls

---

## 3. UX Points

From UX_DESIGN - implement exactly:

### Tab Navigation
- [ ] Two tabs: "Profile" and "Resume Generator"
- [ ] Active tab underlined
- [ ] Clicking tab switches view

### Job Description Input View
- [ ] Title: "Generate Tailored Resume"
- [ ] Instructions: "Paste a job description below. We'll analyze it and create a resume highlighting your most relevant experience."
- [ ] Textarea with placeholder: "Paste job description here..."
- [ ] Character counter: "0 / 100 minimum characters"
- [ ] Button: "Generate Resume"

### Loading State
- [ ] Progress bar displayed
- [ ] Status text: "Analyzing job description..."
- [ ] Status text: "Matching your experience..."
- [ ] Status text: "Composing tailored resume..."
- [ ] Cancel button available
- [ ] Job description locked (read-only, dimmed)

### Result View
- [ ] "Back to Input" link (top left)
- [ ] Match score displayed (top right): "Match Score: XX%"
- [ ] Match score color: green (80-100%), default (60-79%), orange (0-59%)
- [ ] Job title and company displayed
- [ ] Generated date displayed

### Requirements Analysis Card
- [ ] Collapsible (default expanded)
- [ ] Header: "Job Requirements"
- [ ] Required Skills with match indicators (checkmark/X)
- [ ] Preferred Skills with match indicators
- [ ] Experience requirement with match indicator
- [ ] Education requirement with match indicator

### Resume Preview Sections
- [ ] Personal Info section (always visible)
- [ ] Work Experience section with [ON]/[OFF] toggle
- [ ] Skills section with [ON]/[OFF] toggle
- [ ] Education section with [ON]/[OFF] toggle
- [ ] Projects section with [ON]/[OFF] toggle
- [ ] When OFF: shows "(Section hidden from resume)"
- [ ] Each section collapsible with [collapse] toggle

### Work Experience Items
- [ ] Numbered list (1, 2, 3...)
- [ ] Title format: "Senior Developer - Acme Corp"
- [ ] Date format: "Jan 2020 - Present"
- [ ] Description displayed
- [ ] Match reasons displayed: "Match: Python, AWS, Team Leadership"
- [ ] Edit button available

### Inline Edit
- [ ] Clicking Edit expands textarea inline
- [ ] Only description is editable
- [ ] Save/Cancel buttons appear
- [ ] "Saved" indicator after save (fades after 2 sec)

### History Section
- [ ] Header: "History"
- [ ] Collapsible
- [ ] Empty state: "No resumes generated yet."
- [ ] Each item shows: job title, company, date, match score
- [ ] Delete button on each item
- [ ] Click item loads resume

### Regenerate
- [ ] "Regenerate" button at bottom of preview

### Error Messages (exact text)
- [ ] Empty input: "Please paste a job description (at least 100 characters)"
- [ ] Profile incomplete: "Your profile needs work experience before you can generate a tailored resume."
- [ ] API error: "Could not generate resume. Please try again."
- [ ] Timeout: "This is taking longer than expected..."
- [ ] Invalid JD: "This doesn't appear to be a job description. Please paste a complete job posting."
- [ ] Save failed: "Could not save changes. Please try again."

### Visual Design
- [ ] System font stack (same as Feature 1)
- [ ] Text color: `#1a1a1a`
- [ ] Background: `#ffffff`
- [ ] Borders: `#e0e0e0`
- [ ] Primary action: `#0066cc`
- [ ] Error: `#cc0000`
- [ ] Success/Match: `#008800`
- [ ] Warning: `#cc6600`
- [ ] Progress bar: 4px height, `#0066cc` fill

---

## 4. API Endpoint Points

From IMPL_PLAN:

### POST /api/resumes/generate
- [ ] Accepts `job_description` in request body
- [ ] Validates min 100 characters
- [ ] Returns full resume object with match_score, job_analysis, resume
- [ ] Returns 400 if profile incomplete
- [ ] Returns 400 if job description invalid

### GET /api/resumes
- [ ] Returns list of generated resumes (history)
- [ ] Sorted by created_at DESC
- [ ] Includes: id, job_title, company_name, match_score, created_at

### GET /api/resumes/{id}
- [ ] Returns full resume object
- [ ] Returns 404 if not found

### PUT /api/resumes/{id}
- [ ] Accepts resume content updates
- [ ] Updates only provided fields
- [ ] Returns updated resume
- [ ] Returns 404 if not found

### DELETE /api/resumes/{id}
- [ ] Returns 204 No Content
- [ ] Returns 404 if not found

### GET /api/profile/complete
- [ ] Returns aggregated profile (all sections)
- [ ] Includes: personal_info, work_experiences, education, skills, projects

---

## 5. Test Points

From FEATURE_SPEC scenarios:

### Unit Tests - LLM Service
- [ ] Test prompt construction with profile data
- [ ] Test response parsing (valid JSON)
- [ ] Test response parsing (invalid JSON - error handling)
- [ ] Test error handling (APIConnectionError)
- [ ] Test error handling (RateLimitError)

### Unit Tests - Resume Generator Service
- [ ] Test generate with valid profile
- [ ] Test generate with empty profile (error)
- [ ] Test save resume to database

### Unit Tests - Profile Service
- [ ] Test get_complete aggregates all sections
- [ ] Test completeness check (has work experience)

### API Endpoint Tests
- [ ] POST /api/resumes/generate - success (mocked LLM)
- [ ] POST /api/resumes/generate - empty JD (400)
- [ ] POST /api/resumes/generate - short JD (400)
- [ ] POST /api/resumes/generate - no profile (400)
- [ ] GET /api/resumes - returns list
- [ ] GET /api/resumes - empty list
- [ ] GET /api/resumes/{id} - success
- [ ] GET /api/resumes/{id} - not found (404)
- [ ] PUT /api/resumes/{id} - success
- [ ] PUT /api/resumes/{id} - not found (404)
- [ ] DELETE /api/resumes/{id} - success (204)
- [ ] DELETE /api/resumes/{id} - not found (404)
- [ ] GET /api/profile/complete - returns all sections

### Database Tests
- [ ] job_descriptions table created
- [ ] generated_resumes table created
- [ ] Foreign key constraint works
- [ ] Index on created_at exists

---

## 6. Accessibility Points

From UX_DESIGN:

- [ ] Tab navigation keyboard accessible (Tab key cycles)
- [ ] All buttons keyboard accessible (Enter activates)
- [ ] Focus states visible (2px blue outline)
- [ ] Textarea has visible label "Job Description *"
- [ ] Character counter announced to screen readers
- [ ] Progress status announced via aria-live
- [ ] Toggle buttons have aria-pressed state
- [ ] Error messages linked with aria-describedby
- [ ] Match indicators have text (not color only): checkmark/X
- [ ] History items keyboard navigable
- [ ] Escape cancels editing

---

## 7. Database Schema Points

- [ ] job_descriptions table:
  - [ ] id INTEGER PRIMARY KEY AUTOINCREMENT
  - [ ] raw_text TEXT NOT NULL
  - [ ] parsed_data TEXT (nullable)
  - [ ] created_at TEXT DEFAULT CURRENT_TIMESTAMP

- [ ] generated_resumes table:
  - [ ] id INTEGER PRIMARY KEY AUTOINCREMENT
  - [ ] job_description_id INTEGER NOT NULL (FK)
  - [ ] job_title TEXT (nullable)
  - [ ] company_name TEXT (nullable)
  - [ ] match_score REAL (nullable)
  - [ ] resume_content TEXT NOT NULL
  - [ ] created_at TEXT DEFAULT CURRENT_TIMESTAMP
  - [ ] updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  - [ ] FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)

- [ ] Index: idx_generated_resumes_created on created_at DESC

---

## 8. File Creation Points

### Backend Files
- [ ] `services/__init__.py` created
- [ ] `services/llm.py` created
- [ ] `services/resume_generator.py` created
- [ ] `services/profile.py` created
- [ ] `routes/resumes.py` created

### Frontend Files
- [ ] `src/components/TabNav.svelte` created
- [ ] `src/components/ProfileEditor.svelte` created
- [ ] `src/components/ResumeGenerator.svelte` created
- [ ] `src/components/JobDescriptionInput.svelte` created
- [ ] `src/components/ResumePreview.svelte` created
- [ ] `src/components/RequirementsAnalysis.svelte` created
- [ ] `src/components/ResumeSection.svelte` created
- [ ] `src/components/ResumeHistory.svelte` created
- [ ] `src/components/ProgressBar.svelte` created

### Test Files
- [ ] `tests/test_resumes.py` created
- [ ] `tests/test_llm_service.py` created
- [ ] `tests/test_resume_generator.py` created

### Modified Files
- [ ] `main.py` - loads dotenv, includes resumes router
- [ ] `database.py` - adds new tables
- [ ] `schemas.py` - adds resume schemas
- [ ] `src/App.svelte` - adds tab navigation
- [ ] `src/lib/api.js` - adds resume API functions
- [ ] `src/styles/main.scss` - adds new component styles
- [ ] `tests/conftest.py` - adds resume fixtures
- [ ] `requirements.txt` - adds new dependencies
- [ ] `.gitignore` - adds .env

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v3-close`.

**Total Checklist Points:**
- Ecosystem: 6
- Dependencies: 11
- Syntax: 17
- UX: 52
- API: 17
- Tests: 26
- Accessibility: 11
- Database: 14
- Files: 24

**Total: 178 verification points**

---

*Contract for /v3-implement*
