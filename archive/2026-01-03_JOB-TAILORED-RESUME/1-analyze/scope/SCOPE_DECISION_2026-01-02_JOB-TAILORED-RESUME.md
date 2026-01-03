# Scope Decision: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Classification:** Single Feature
**Parent Epic:** AI-RESUME-SYSTEM (Feature 3 of 5)

## Request

> Feature 3: Job-Tailored Resume Generation - Paste a job description, AI analyzes it and generates a tailored resume highlighting relevant experiences, reordering sections, emphasizing matching skills. Core value proposition - one profile, infinite tailored resumes. Dependencies: Feature 1 (profile data) is complete. Scope: Job description parser, relevance scoring, resume composition engine, preview UI.

## Size Indicators

- [ ] Contains "and" connecting distinct capabilities
- [ ] Affects multiple user personas
- [ ] Spans multiple domains
- [x] Has multiple independent acceptance criteria
- [ ] User mentions phases or iterations
- [x] Would require > 10 files changed

**Score: 2/6 - Borderline → Single Feature**

## Decision

Proceed as single feature because:
- Already scoped as Feature 3 in parent epic breakdown
- Cohesive workflow: paste JD → analyze → generate → preview (one user journey)
- Single user persona: job seeker tailoring their resume
- Single domain: resume generation (AI/LLM is implementation, not separate domain)
- Clear deliverable: a working resume tailoring interface

## Feature Name

**JOB-TAILORED-RESUME**

(Used in all subsequent artifacts for this feature)

## Feature Boundary

**In Scope:**
- Job description input UI (paste text area)
- Job description parsing/analysis (extract requirements, skills, keywords)
- Relevance scoring (match profile entries to JD requirements)
- Resume composition engine (select, reorder, emphasize relevant content)
- Tailored resume preview UI
- LLM integration for analysis and generation

**Out of Scope (Other Features):**
- PDF export (Feature 4)
- AI profile enhancement/interviews (Feature 2)
- Application tracking/versioning (Feature 5)
- Profile data CRUD (Feature 1 - already complete)

## Dependencies

- **Feature 1: Profile Data Foundation** - COMPLETE
  - Uses existing profile data (personal info, work experience, education, skills, projects)
  - Uses existing API endpoints to fetch profile
  - Uses existing database schema

## Next Step

→ Proceed to `/v3-requirements` to define detailed specifications
