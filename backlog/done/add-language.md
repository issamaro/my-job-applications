# Add Language Section with CEFR Levels

**Size:** M (Medium)
**Date:** 2026-01-07
**Estimated Files:** 10-12
**Dependencies:** None

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Intent type | A - Define precisely | Clear requirements, straightforward implementation |
| Confidence | A - Very confident | User knows exactly what they want - CEFR levels |
| Scope validation | A - Yes, proceed | No revisions needed |

## Description

Add a Languages section to the resume/CV application. Users can add languages they speak along with their proficiency level using the CEFR (Common European Framework of Reference for Languages) scale: A1, A2, B1, B2, C1, C2. This section will be included in profile management, resume generation, and PDF export.

## Scope (IN)

- Create `Language` Pydantic schema with fields: id, name, level (CEFR enum: A1/A2/B1/B2/C1/C2)
- Create `languages` database table
- Create CRUD API endpoints at `/api/languages`
- Create `Languages.svelte` component for profile management
- Add language section to profile page
- Include languages in resume generation (ResumeContent schema)
- Display languages in ResumePreview.svelte with toggle
- Include languages in PDF export (both classic and modern templates)
- Validate CEFR levels on backend

## Out of Scope (NOT)

- Language flags/icons
- Native speaker designation (beyond C2)
- Language certificates (e.g., TOEFL, IELTS scores)
- Multiple proficiency types (speaking, reading, writing separately)
- AI/LLM matching of languages to job requirements

## Success Criteria

- [ ] User can add a language with a CEFR level (A1-C2) from the profile page
- [ ] User can edit and delete existing language entries
- [ ] Languages appear in generated resumes
- [ ] Languages section can be toggled on/off in resume preview
- [ ] Languages appear in exported PDF (both templates)
- [ ] Invalid CEFR levels are rejected by the API
- [ ] Languages persist in database across sessions

## Technical Notes

- Follow existing section patterns (Skills, Education, Projects)
- CEFR levels: A1 (Beginner), A2 (Elementary), B1 (Intermediate), B2 (Upper Intermediate), C1 (Advanced), C2 (Proficient)
- Use same ResumeSection wrapper component for consistency
- Consider display order by proficiency level (C2 first) or user-defined order

## Files to Modify

1. `schemas.py` - Add Language, LanguageCreate, ResumeLanguage schemas
2. `database.py` - Add languages table in init_db()
3. `routes/languages.py` - New file with CRUD endpoints
4. `routes/__init__.py` - Register languages router
5. `main.py` - Include languages router
6. `src/lib/api.js` - Add language API functions
7. `src/components/Languages.svelte` - New component
8. `src/routes/profile/+page.svelte` - Add Languages section
9. `services/resume_generator.py` - Include languages in ResumeContent
10. `src/components/ResumePreview.svelte` - Display languages section
11. PDF template files - Add languages section rendering
