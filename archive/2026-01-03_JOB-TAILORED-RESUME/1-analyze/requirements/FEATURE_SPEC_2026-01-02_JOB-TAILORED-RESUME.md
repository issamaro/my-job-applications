# Feature Spec: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Status:** Draft
**Feature Name:** JOB-TAILORED-RESUME

---

## 1. Problem Statement

### User Request
> Paste a job description, AI analyzes it and generates a tailored resume highlighting relevant experiences, reordering sections, emphasizing matching skills. Core value proposition - one profile, infinite tailored resumes.

### Pain Point
Users have a complete professional profile but struggle to:
- Identify which experiences are most relevant for a specific job
- Reword their achievements to match job requirements
- Prioritize and reorder content for maximum impact
- Manually customize resumes for each application (time-consuming, error-prone)

### User Persona
**Job Seeker** - Someone with a completed profile who wants to generate targeted resumes quickly and effectively for specific job opportunities.

---

## 2. BDD Scenarios

```gherkin
Feature: Job-Tailored Resume Generation
  As a job seeker
  I want to paste a job description and get a tailored resume
  So that I can quickly create targeted applications without manual customization

  # === CORE FLOW ===

  Scenario: Generate tailored resume from job description
    Given I have a completed profile with work experiences, skills, and education
    And I am on the resume generation page
    When I paste a job description into the input field
    And I click "Generate Resume"
    Then I see a loading indicator while the AI processes
    And I see a tailored resume preview within 30 seconds
    And the preview highlights which profile items were selected
    And I see a relevance score for the overall match

  Scenario: View job requirements analysis
    Given I have pasted a job description
    When the AI completes analysis
    Then I see extracted requirements categorized as:
      | Category | Examples |
      | Required Skills | Python, AWS, SQL |
      | Preferred Skills | Kubernetes, Terraform |
      | Experience Level | 5+ years |
      | Education | Bachelor's in CS |
    And each requirement shows whether my profile matches it

  Scenario: Preview tailored resume content
    Given the AI has generated a tailored resume
    When I view the preview
    Then I see my personal info at the top
    And I see work experiences reordered by relevance to the job
    And I see skills filtered to those matching the job
    And I see education if required by the job
    And I see projects if relevant to the job
    And each section shows why it was included (match reason)

  # === PROFILE REQUIREMENTS ===

  Scenario: Attempt generation with incomplete profile
    Given I have not entered any work experiences
    When I try to generate a tailored resume
    Then I see an error message "Please add at least one work experience to generate a resume"
    And I see a link to the profile editor

  Scenario: Attempt generation with empty job description
    Given I am on the resume generation page
    When I click "Generate Resume" without entering a job description
    Then I see a validation error "Please paste a job description"
    And the input field is highlighted

  # === EDITING & CUSTOMIZATION ===

  Scenario: Edit generated resume content
    Given the AI has generated a tailored resume
    When I click on a work experience entry
    Then I can edit the description text
    And my edits are preserved in this tailored version
    And my original profile data is not modified

  Scenario: Toggle sections on/off
    Given the AI has generated a tailored resume
    When I click the toggle for "Projects" section
    Then the Projects section is hidden from the resume
    And I can toggle it back on

  Scenario: Reorder work experiences manually
    Given the AI has generated a tailored resume
    When I drag a work experience to a different position
    Then the order updates in the preview
    And the new order is preserved

  # === REGENERATION ===

  Scenario: Regenerate with different emphasis
    Given I have a generated resume
    When I adjust the "Experience vs Skills" emphasis slider
    And I click "Regenerate"
    Then the AI produces a new version with adjusted priorities
    And I can compare with the previous version

  Scenario: Regenerate after profile update
    Given I have a generated resume
    And I add a new skill to my profile
    When I click "Regenerate"
    Then the new skill is considered in the analysis
    And the resume updates if the skill is relevant

  # === ERROR HANDLING ===

  Scenario: Handle AI service unavailable
    Given the AI service is temporarily unavailable
    When I try to generate a tailored resume
    Then I see an error message "Resume generation is temporarily unavailable. Please try again later."
    And my job description is preserved in the input
    And I see a "Retry" button

  Scenario: Handle timeout during generation
    Given I have submitted a job description
    And the AI takes longer than 60 seconds
    Then I see a message "This is taking longer than expected..."
    And I have the option to continue waiting or cancel

  Scenario: Handle invalid job description
    Given I paste text that is not a job description
    When the AI attempts to analyze it
    Then I see a message "This doesn't appear to be a job description. Please paste a complete job posting."
    And I can edit and retry

  # === HISTORY ===

  Scenario: View generation history
    Given I have generated multiple tailored resumes
    When I click "History"
    Then I see a list of previous generations
    And each entry shows the job title, company (if detected), and date
    And I can click to view or re-edit any previous resume

  Scenario: Delete a generated resume from history
    Given I have generated resumes in history
    When I click delete on a history item
    And I confirm the deletion
    Then the item is removed from history
    And my profile data is unaffected
```

---

## 3. Requirements

### Must Have (MVP)

#### Backend
- [ ] **REQ-B1**: API endpoint to submit job description for analysis (`POST /api/resumes/generate`)
- [ ] **REQ-B2**: LLM integration for job description parsing (extract skills, requirements, experience level)
- [ ] **REQ-B3**: Relevance scoring algorithm (match profile items to job requirements)
- [ ] **REQ-B4**: Resume composition service (select, order, and format profile content)
- [ ] **REQ-B5**: API endpoint to fetch profile data for resume generation (aggregate all sections)
- [ ] **REQ-B6**: Database table for generated resumes (store job description, generated content, timestamps)
- [ ] **REQ-B7**: API endpoint to retrieve generated resume (`GET /api/resumes/{id}`)
- [ ] **REQ-B8**: API endpoint to list resume history (`GET /api/resumes`)

#### Frontend
- [ ] **REQ-F1**: Job description input page with large textarea
- [ ] **REQ-F2**: "Generate Resume" button with loading state
- [ ] **REQ-F3**: Resume preview component showing tailored content
- [ ] **REQ-F4**: Job requirements analysis display (extracted skills, experience level)
- [ ] **REQ-F5**: Match indicators showing which profile items align with requirements
- [ ] **REQ-F6**: Overall relevance/match score display
- [ ] **REQ-F7**: Navigation between job input and resume preview
- [ ] **REQ-F8**: Error states for validation, API errors, and timeouts

#### Validation
- [ ] **REQ-V1**: Require non-empty job description (min 100 characters)
- [ ] **REQ-V2**: Require at least one work experience in profile
- [ ] **REQ-V3**: Handle LLM response validation (ensure structured output)

### Should Have (Enhancement)

- [ ] **REQ-S1**: Edit generated resume content (modify descriptions without changing profile)
- [ ] **REQ-S2**: Toggle sections on/off in generated resume
- [ ] **REQ-S3**: Manual reordering of work experiences (drag-and-drop)
- [ ] **REQ-S4**: Resume history list with date and detected job title
- [ ] **REQ-S5**: Regenerate button to create new version
- [ ] **REQ-S6**: Delete generated resume from history
- [ ] **REQ-S7**: Show "why included" reasoning for each resume item

### Won't Have (Out of Scope - Future Features)

- PDF export (Feature 4)
- AI profile enhancement/interviews (Feature 2)
- Application tracking with status workflow (Feature 5)
- Multiple template/style options
- Job URL fetching (auto-paste from URL)
- Cover letter generation
- Multi-user support / authentication

---

## 4. Technical Context

### Existing Infrastructure (From Feature 1)

| Component | Technology | Notes |
|-----------|------------|-------|
| Backend | FastAPI + Python 3.x | Routes in `/routes/*.py` |
| Database | SQLite | Tables: personal_info, work_experiences, education, skills, projects |
| Frontend | Svelte 5 (runes) | Components in `/src/components/*.svelte` |
| Styling | Sass | `/src/styles/main.scss` |
| Build | Rollup | Config in `rollup.config.js` |
| API Client | `/src/lib/api.js` | Centralized fetch wrapper |

### New Infrastructure Required

| Component | Technology | Notes |
|-----------|------------|-------|
| LLM Integration | Anthropic Claude API | `anthropic` Python SDK for job description analysis |
| Environment Config | .env / python-dotenv | `ANTHROPIC_API_KEY` storage |
| New DB Tables | SQLite | job_descriptions, generated_resumes |

---

## 5. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| User has Anthropic API key | Architecture | User sets `ANTHROPIC_API_KEY` in `.env`; app shows clear error if missing |
| Single-user system continues | Architecture | No auth required; singleton pattern like personal_info |
| LLM can reliably extract structured data | Library | Will need robust prompt engineering and response parsing |
| Profile data is sufficient for resume | UX | User has completed Feature 1 profile entry |
| English language only | UX | Job descriptions and resumes in English |
| Text-only job descriptions | UX | No image/PDF parsing of job postings |
| Resume output is structured data | Architecture | JSON structure; PDF rendering is Feature 4 |
| Generation takes < 30 seconds typical | Architecture | Async with timeout handling for edge cases |

---

## 6. Data Model (Proposed)

### New Tables

```sql
-- Store job descriptions submitted for analysis
CREATE TABLE job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    parsed_data TEXT,  -- JSON: extracted requirements, skills, etc.
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Store generated resumes
CREATE TABLE generated_resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_description_id INTEGER NOT NULL,
    job_title TEXT,           -- Extracted from JD
    company_name TEXT,        -- Extracted from JD
    match_score REAL,         -- 0-100 relevance score
    resume_content TEXT NOT NULL,  -- JSON: structured resume data
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)
);
```

### Resume Content Structure (JSON)

```json
{
  "personal_info": { ... },
  "summary": "AI-generated tailored summary",
  "work_experiences": [
    {
      "id": 1,
      "included": true,
      "order": 1,
      "original_description": "...",
      "tailored_description": "...",
      "match_reasons": ["Python experience", "Team leadership"]
    }
  ],
  "education": [ ... ],
  "skills": [
    { "name": "Python", "matched": true },
    { "name": "JavaScript", "matched": false, "included": false }
  ],
  "projects": [ ... ]
}
```

---

## 7. API Endpoints (Proposed)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resumes/generate` | Submit JD, returns generated resume |
| GET | `/api/resumes` | List all generated resumes (history) |
| GET | `/api/resumes/{id}` | Get specific generated resume |
| PUT | `/api/resumes/{id}` | Update generated resume (edits) |
| DELETE | `/api/resumes/{id}` | Delete generated resume |
| GET | `/api/profile/complete` | Get aggregated profile for resume generation |

---

## 8. Design Decisions (Resolved)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **LLM Provider** | Anthropic Claude | Consistent with project tooling, excellent at structured extraction |
| **API Key Management** | User provides own key | User sets `ANTHROPIC_API_KEY` in `.env`. No shared costs. |
| **Prompt Strategy** | Single prompt | Analysis + generation in one call. Simpler, fewer API calls. |
| **Caching** | No caching | Always call LLM. Profile may change between generations. |
| **Match Score** | LLM-generated | Ask LLM to provide score as part of analysis. More holistic. |

---

## 9. UI Flow (High-Level)

```
┌─────────────────────────────────────────────────────────────┐
│                    Resume Generator                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Job Description Input]                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Paste job description here...                      │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Generate Resume]                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Resume Preview                    Match: 85%    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Requirements Analysis                                      │
│  ├─ Required: Python ✓, AWS ✓, SQL ✓                       │
│  ├─ Preferred: Kubernetes ✗, Docker ✓                      │
│  └─ Experience: 5+ years ✓                                 │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  [Personal Info]                                            │
│  John Doe | john@email.com | San Francisco                  │
│                                                             │
│  [Work Experience]                               [toggle]   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Senior Developer @ TechCorp          2020-Present   │   │
│  │ "Led Python backend development..."                 │   │
│  │ Match: Python, Team Leadership                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Skills]                                        [toggle]   │
│  Python • AWS • SQL • Docker • React                        │
│                                                             │
│  [Edit] [Regenerate] [Back to Input]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Next: /v3-ux for detailed UI/UX design*
