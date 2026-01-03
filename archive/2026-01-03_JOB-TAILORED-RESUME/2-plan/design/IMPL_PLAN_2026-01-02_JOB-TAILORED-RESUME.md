# Implementation Plan: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-02_JOB-TAILORED-RESUME.md

---

## 1. Affected Files

### Config/Dependencies

| File | Change | Description |
|------|--------|-------------|
| `requirements.txt` | Modify | Add `anthropic>=0.40.0`, `python-dotenv>=1.0.0` |
| `.env` | Create | Add `ANTHROPIC_API_KEY=` |
| `.env.example` | Create | Template without secrets |
| `.gitignore` | Modify | Add `.env` |

### Backend

| File | Change | Description |
|------|--------|-------------|
| `main.py` | Modify | Load dotenv, add resumes router |
| `database.py` | Modify | Add job_descriptions, generated_resumes tables |
| `schemas.py` | Modify | Add resume generation request/response schemas |
| `services/__init__.py` | Create | Package init |
| `services/llm.py` | Create | Anthropic client wrapper, prompt construction |
| `services/resume_generator.py` | Create | Resume composition logic |
| `services/profile.py` | Create | Aggregate profile data for LLM |
| `routes/resumes.py` | Create | Resume generation endpoints |

### Frontend

| File | Change | Description |
|------|--------|-------------|
| `src/App.svelte` | Modify | Add tab navigation, conditional view rendering |
| `src/components/TabNav.svelte` | Create | Tab navigation component |
| `src/components/ProfileEditor.svelte` | Create | Wrapper for existing profile sections |
| `src/components/ResumeGenerator.svelte` | Create | Main resume generator view |
| `src/components/JobDescriptionInput.svelte` | Create | Textarea with validation |
| `src/components/ResumePreview.svelte` | Create | Generated resume display |
| `src/components/RequirementsAnalysis.svelte` | Create | Job requirements with match indicators |
| `src/components/ResumeSection.svelte` | Create | Toggleable resume section |
| `src/components/ResumeHistory.svelte` | Create | List of generated resumes |
| `src/components/ProgressBar.svelte` | Create | Loading progress indicator |
| `src/lib/api.js` | Modify | Add resume generation API functions |
| `src/styles/main.scss` | Modify | Add styles for new components |

### Tests

| File | Change | Description |
|------|--------|-------------|
| `tests/test_resumes.py` | Create | Resume endpoint tests |
| `tests/test_llm_service.py` | Create | LLM service tests (mocked) |
| `tests/test_resume_generator.py` | Create | Resume composition tests |
| `tests/conftest.py` | Modify | Add fixtures for resume testing |

---

## 2. Database Changes

```sql
-- New table: Store submitted job descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    parsed_data TEXT,  -- JSON: extracted requirements
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- New table: Store generated resumes
CREATE TABLE IF NOT EXISTS generated_resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_description_id INTEGER NOT NULL,
    job_title TEXT,
    company_name TEXT,
    match_score REAL,
    resume_content TEXT NOT NULL,  -- JSON: structured resume
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)
);

-- Index for history queries
CREATE INDEX IF NOT EXISTS idx_generated_resumes_created
ON generated_resumes(created_at DESC);
```

---

## 3. Implementation Approach

### Service Pattern

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  routes/        │────▶│  services/       │────▶│  database.py    │
│  resumes.py     │     │  resume_generator│     │                 │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼───────┐        ┌────────▼────────┐
            │ services/     │        │ services/       │
            │ llm.py        │        │ profile.py      │
            └───────────────┘        └─────────────────┘
```

- **routes/resumes.py**: HTTP layer, request validation, response formatting
- **services/resume_generator.py**: Orchestrates profile fetch, LLM call, resume composition
- **services/llm.py**: Anthropic client, prompt construction, response parsing
- **services/profile.py**: Aggregates all profile sections into single structure

### LLM Integration

**Single-prompt approach:**
1. Construct prompt with: job description + full profile data
2. Ask Claude to return structured JSON with:
   - Extracted job requirements (skills, experience, education)
   - Match analysis (which profile items match which requirements)
   - Tailored resume content (reordered, emphasized)
   - Overall match score (0-100)

**Prompt structure:**
```
System: You are a resume optimization expert. Analyze the job description
and profile, then generate a tailored resume.

User:
JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{profile_json}

Return a JSON object with this structure:
{
  "job_analysis": { ... },
  "match_score": 85,
  "resume": { ... }
}
```

### Validation

| Layer | Validation |
|-------|------------|
| Frontend | Character count (100+ min), non-empty |
| Route | Pydantic schema validation |
| Service | Profile completeness check (has work experience) |
| LLM | Response structure validation |

### Error Handling

| Error | Detection | User Message | Recovery |
|-------|-----------|--------------|----------|
| No API key | Startup/first call | "API key not configured" | Check .env |
| API connection | Anthropic exception | "Could not connect to AI service" | Retry button |
| Rate limit | 429 response | "Service busy, try again later" | Auto-retry with backoff |
| Invalid JD | LLM analysis | "This doesn't look like a job description" | Edit and retry |
| Timeout | 60s elapsed | "Taking longer than expected" | Keep waiting or cancel |
| No profile | Service check | "Add work experience first" | Link to Profile tab |

### Frontend State Management

```svelte
// ResumeGenerator.svelte
let view = $state('input');  // 'input' | 'loading' | 'preview'
let currentResume = $state(null);
let history = $state([]);
let error = $state(null);
```

**View transitions:**
```
input ──[Generate]──▶ loading ──[Success]──▶ preview
                          │                      │
                          └──[Error]──▶ input    │
                                                 │
preview ──[Back]──▶ input ◀──────────────────────┘
preview ──[Regenerate]──▶ loading
```

---

## 4. Implementation Order

### Phase 1: Backend Foundation

1. [ ] `requirements.txt` - Add anthropic, python-dotenv
2. [ ] `.env`, `.env.example`, `.gitignore` - Environment setup
3. [ ] `database.py` - Add new tables to init_db()
4. [ ] `schemas.py` - Add Pydantic schemas for resumes

### Phase 2: Backend Services

5. [ ] `services/__init__.py` - Create package
6. [ ] `services/profile.py` - Profile aggregation service
7. [ ] `services/llm.py` - Anthropic client and prompts
8. [ ] `services/resume_generator.py` - Resume composition orchestration

### Phase 3: Backend Routes

9. [ ] `routes/resumes.py` - All resume endpoints
10. [ ] `main.py` - Load dotenv, register router

### Phase 4: Backend Tests

11. [ ] `tests/conftest.py` - Add resume fixtures
12. [ ] `tests/test_resumes.py` - Endpoint tests
13. [ ] `tests/test_llm_service.py` - LLM service tests (mocked)
14. [ ] `tests/test_resume_generator.py` - Composition tests

### Phase 5: Frontend Foundation

15. [ ] `src/lib/api.js` - Add resume API functions
16. [ ] `src/components/TabNav.svelte` - Tab navigation
17. [ ] `src/components/ProfileEditor.svelte` - Wrap existing sections

### Phase 6: Frontend Resume Generator

18. [ ] `src/components/ProgressBar.svelte` - Loading indicator
19. [ ] `src/components/JobDescriptionInput.svelte` - Input with validation
20. [ ] `src/components/RequirementsAnalysis.svelte` - Job requirements display
21. [ ] `src/components/ResumeSection.svelte` - Toggleable section
22. [ ] `src/components/ResumePreview.svelte` - Full preview
23. [ ] `src/components/ResumeHistory.svelte` - History list
24. [ ] `src/components/ResumeGenerator.svelte` - Main view orchestrator

### Phase 7: Integration

25. [ ] `src/App.svelte` - Integrate tabs and views
26. [ ] `src/styles/main.scss` - Add new component styles

### Phase 8: Final Testing

27. [ ] Manual testing - All user journeys
28. [ ] Error scenario testing - All error states

---

## 5. API Endpoints Detail

### POST /api/resumes/generate

**Request:**
```json
{
  "job_description": "Senior Software Engineer at TechCorp..."
}
```

**Response (Success):**
```json
{
  "id": 1,
  "job_title": "Senior Software Engineer",
  "company_name": "TechCorp",
  "match_score": 78.5,
  "job_analysis": {
    "required_skills": [
      {"name": "Python", "matched": true},
      {"name": "AWS", "matched": true}
    ],
    "preferred_skills": [
      {"name": "Kubernetes", "matched": false}
    ],
    "experience_years": {"required": 5, "matched": true},
    "education": {"required": "Bachelor's CS", "matched": true}
  },
  "resume": {
    "personal_info": {...},
    "summary": "Tailored summary...",
    "work_experiences": [
      {
        "id": 1,
        "company": "Acme Corp",
        "title": "Senior Developer",
        "description": "Tailored description...",
        "match_reasons": ["Python", "Team Leadership"],
        "included": true,
        "order": 1
      }
    ],
    "skills": [
      {"name": "Python", "matched": true, "included": true}
    ],
    "education": [...],
    "projects": [...]
  },
  "created_at": "2026-01-02T14:30:00Z"
}
```

**Response (Error):**
```json
{
  "detail": "Please add at least one work experience to generate a resume"
}
```

### GET /api/resumes

**Response:**
```json
[
  {
    "id": 1,
    "job_title": "Senior Software Engineer",
    "company_name": "TechCorp",
    "match_score": 78.5,
    "created_at": "2026-01-02T14:30:00Z"
  }
]
```

### GET /api/resumes/{id}

Returns full resume object (same as generate response).

### PUT /api/resumes/{id}

**Request:**
```json
{
  "resume": {
    "work_experiences": [
      {"id": 1, "description": "Updated description...", "included": true}
    ]
  }
}
```

### DELETE /api/resumes/{id}

Returns 204 No Content.

### GET /api/profile/complete

Aggregates all profile data for LLM:
```json
{
  "personal_info": {...},
  "work_experiences": [...],
  "education": [...],
  "skills": [...],
  "projects": [...]
}
```

---

## 6. LLM Prompt Design

### System Prompt

```
You are an expert resume writer and career coach. Your task is to analyze
a job description and a candidate's profile, then create a tailored resume
that highlights the most relevant qualifications.

You must return valid JSON matching the specified schema.

Guidelines:
- Extract key requirements from the job description
- Match candidate qualifications to job requirements
- Reorder work experiences by relevance (most relevant first)
- Enhance descriptions to emphasize matching skills (but never fabricate)
- Calculate a realistic match score (0-100) based on requirement coverage
- Be honest about gaps - don't claim matches that don't exist
```

### User Prompt Template

```
Analyze this job description and create a tailored resume from the candidate profile.

## JOB DESCRIPTION
{job_description}

## CANDIDATE PROFILE
{profile_json}

## REQUIRED OUTPUT FORMAT
Return a JSON object with exactly this structure:
{schema}

Important:
- Only include profile items that are relevant to this job
- Reorder work experiences by relevance (most relevant first)
- For each included item, explain why it matches (match_reasons)
- Be accurate with the match_score - it should reflect actual qualification coverage
```

---

## 7. Risks and Mitigations

| Risk | L | I | Mitigation |
|------|---|---|------------|
| LLM returns invalid JSON | Med | High | Strict schema validation, retry with correction prompt |
| LLM hallucinates qualifications | Low | High | Prompt emphasizes honesty, validate against profile |
| API costs exceed budget | Med | Med | Use sonnet (not opus), set max_tokens limit |
| Slow generation (>30s) | Med | Med | Progress indicator, timeout with user choice |
| User has no API key | High | High | Clear error message, link to Anthropic console |
| Rate limiting | Low | Med | Exponential backoff, queue requests |

---

## 8. File Details

### services/llm.py

```python
# Key responsibilities:
# - Initialize AsyncAnthropic client (singleton)
# - Construct prompts from templates
# - Parse and validate LLM responses
# - Handle Anthropic-specific errors

class LLMService:
    def __init__(self):
        self.client = AsyncAnthropic()

    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict
    ) -> dict:
        # Returns parsed, validated response
```

### services/resume_generator.py

```python
# Key responsibilities:
# - Check profile completeness
# - Fetch profile via profile service
# - Call LLM service
# - Save to database
# - Return structured response

class ResumeGeneratorService:
    async def generate(self, job_description: str) -> GeneratedResume:
        profile = await self.profile_service.get_complete()
        if not profile.work_experiences:
            raise ProfileIncompleteError("...")

        result = await self.llm_service.analyze_and_generate(
            job_description, profile
        )

        return await self.save_resume(result)
```

### services/profile.py

```python
# Key responsibilities:
# - Aggregate all profile sections
# - Format for LLM consumption
# - Check completeness

class ProfileService:
    def get_complete(self) -> CompleteProfile:
        # Returns all sections in one structure
```

---

*Next: /v3-checklist*
