# Cover Letter Generation

## Metadata

| Field | Value |
|-------|-------|
| Size | M (Medium) |
| Date | 2026-01-07 |
| Estimated Files | ~12 |
| Dependencies | Job Application feature (existing), Resume Generator (existing), LLM Service (existing) |

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Intent type | A) Define precisely | Clear requirements - user knows the workflow they want |
| Confidence | B) Somewhat confident | Open to suggestions on UX details |
| Scope validation | A) Yes, proceed | No revisions needed |

## Description

Add automated cover letter generation to the Job Application workflow. After a user has finalized their resume for a job application, they can generate a tailored cover letter. The system prompts for motivation ("Why do you want to work there?") - if provided, it's incorporated into the letter; if left empty, the AI researches the company and generates an appropriate motivation.

## Scope

### IN

- [ ] "Generate Cover Letter" button visible after resume is generated/finalized
- [ ] Modal prompt with question: "Why do you want to work there?"
- [ ] Two generation paths:
  - User provides answer → incorporate into cover letter
  - User leaves empty → AI researches company and generates motivation
- [ ] Cover letter generation via LLM (Claude API)
- [ ] Cover letter preview component with edit capability
- [ ] Cover letter stored in database, linked to job description
- [ ] PDF export for cover letter

### NOT (Out of Scope)

- Multiple cover letter templates (single format for v1)
- Cover letter versioning/history tracking
- Batch generation for multiple jobs
- Direct email/job board submission integration
- Cover letter comparison between versions

## Success Criteria

- [ ] User can click "Generate Cover Letter" after resume is finalized
- [ ] Modal appears prompting "Why do you want to work there?"
- [ ] Submitting with text uses that text in generation
- [ ] Submitting empty triggers AI company research for motivation
- [ ] Generated cover letter displays in preview
- [ ] User can edit cover letter content inline
- [ ] Cover letter persists (reload shows saved letter)
- [ ] PDF export downloads properly formatted cover letter
- [ ] Cover letter is linked to specific job description in database

## Technical Notes

### Files to Create
- `src/components/CoverLetterGenerator.svelte` - Main component with generate button + modal
- `src/components/CoverLetterPreview.svelte` - Preview with edit capability
- `src/routes/cover_letters.py` - API router
- `src/services/cover_letter_generator.py` - Business logic service

### Files to Modify
- `src/database.py` - Add `generated_cover_letters` table
- `src/schemas.py` - Add cover letter request/response schemas
- `src/main.py` - Register cover letter router
- `src/services/llm.py` - Add cover letter generation prompts
- `src/lib/api.js` - Add cover letter API functions
- `src/components/ResumeGenerator.svelte` or parent - Add cover letter section/tab
- `src/services/pdf_generator.py` - Add cover letter PDF template

### Database Schema (proposed)
```sql
CREATE TABLE generated_cover_letters (
    id INTEGER PRIMARY KEY,
    job_description_id INTEGER REFERENCES job_descriptions(id),
    user_motivation TEXT,  -- null if AI-generated
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Notes

- Follow existing resume generation pattern for consistency
- Company research for AI motivation could use web search or extract from job description company name
- Single cover letter per job description (regenerate overwrites)
