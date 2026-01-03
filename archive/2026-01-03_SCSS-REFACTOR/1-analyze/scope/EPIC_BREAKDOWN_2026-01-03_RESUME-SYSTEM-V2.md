# Epic Breakdown: Resume System V2 Enhancements

**Date:** 2026-01-03
**Classification:** Epic

---

## User Request

> Here are the next features I want to breakdown:
> 1. Sass: refactor/improve strategy
> 2. Save job desc. Ability to edit, save automatically generates a new job tailored resume with new input as saved input. (better traceability)
> 3. User interface more offer-specific (a job desc is pasted => a hiring project is created => tailored resume, cover letter, and hiring questions generated)
> 4. Feature 2 from EPIC_BREAKDOWN: AI Profile Enhancement

---

## Size Indicators

- [x] Contains "and" connecting distinct capabilities
- [x] Affects multiple user personas (job seekers, profile managers)
- [x] Spans multiple domains (styling, job tracking, AI, document generation)
- [x] Has multiple independent acceptance criteria
- [x] User mentions phases or iterations (numbered list of 4 features)
- [x] Would require > 10 files changed

**Score: 6/6 - Clear Epic**

---

## Features Identified

### Feature 1: SCSS Architecture Refactor
- **Description:** Refactor the current monolithic `main.scss` (1,047 lines) into a modular, maintainable architecture. Introduce design tokens, component-scoped styles, and improve organization.
- **Value:** Improved developer experience, easier theming, better maintainability as the app grows
- **Dependencies:** None (foundational improvement)
- **Scope:**
  - Split styles into partials (base, components, layouts, utilities)
  - Extract design tokens (colors, spacing, typography)
  - Component-specific SCSS files
  - Build pipeline adjustments

### Feature 2: Saved Job Descriptions with Auto-Regeneration
- **Description:** Allow users to save and edit job descriptions. When a saved job description is modified, automatically regenerate the tailored resume with the updated input. Track version history for traceability.
- **Value:** Better traceability, ability to refine job descriptions, never lose work
- **Dependencies:** None (builds on existing resume generation)
- **Scope:**
  - Job description CRUD UI (save, edit, delete)
  - Version tracking for job descriptions
  - Auto-regeneration trigger on edit
  - Resume version linking to JD versions

### Feature 3: Hiring Projects (Offer-Centric UI)
- **Description:** Transform the UX from resume-centric to offer-centric. When a job description is pasted, create a "Hiring Project" entity that encompasses: the tailored resume, cover letter, and interview prep questions. Everything for one job application in one place.
- **Value:** Holistic job application management, professional cover letters, interview preparation
- **Dependencies:** Feature 2 recommended (saved JDs enable project concept)
- **Scope:**
  - New `hiring_projects` data model
  - Project dashboard UI
  - Cover letter generation (new LLM prompt)
  - Interview questions generation (new LLM prompt)
  - Project status tracking (applied, interviewing, etc.)

### Feature 4: AI Profile Enhancement
- **Description:** AI interviews the user to fill gaps and improve profile entries. Asks probing questions like "How big was that team?", "What was the measurable impact?". Suggests stronger action verbs and quantified achievements.
- **Value:** Transforms basic entries into compelling, quantified achievements
- **Dependencies:** Uses existing profile data
- **Scope:**
  - Conversational UI component
  - Profile analysis prompts (identify gaps)
  - Improvement suggestion prompts
  - Inline enhancement application
  - Progress tracking for profile quality

---

## Feature Analysis Matrix

| Feature | Complexity | User Value | Dependencies | Risk |
|---------|-----------|------------|--------------|------|
| 1. SCSS Refactor | Medium | Medium | None | Low |
| 2. Saved JDs | Medium | High | None | Low |
| 3. Hiring Projects | High | Very High | Feature 2 | Medium |
| 4. AI Enhancement | High | Very High | None | Medium |

---

## Recommended Order

### Option A: Foundation First (Recommended)

1. **Feature 1: SCSS Refactor** - Clean up technical debt before adding more UI. Makes subsequent features easier to style.

2. **Feature 2: Saved Job Descriptions** - Enables Feature 3 and improves existing workflow. Quick win with high value.

3. **Feature 3: Hiring Projects** - Major UX evolution. Builds on Feature 2's saved JD concept.

4. **Feature 4: AI Profile Enhancement** - Independent quality multiplier. Can be done anytime but most impactful after core workflow is solid.

### Option B: Value First

1. **Feature 2: Saved Job Descriptions** - Immediate improvement to existing workflow

2. **Feature 3: Hiring Projects** - Maximum user value, complete job application solution

3. **Feature 4: AI Profile Enhancement** - Improve input quality

4. **Feature 1: SCSS Refactor** - Technical improvement when convenient

### Option C: AI Focus

1. **Feature 4: AI Profile Enhancement** - Improve profile quality first

2. **Feature 2: Saved Job Descriptions** - Better JD management

3. **Feature 3: Hiring Projects** - Full solution with better inputs

4. **Feature 1: SCSS Refactor** - Technical cleanup

---

## User Action Required

**Select which feature to build first:**

| # | Feature | Quick Description |
|---|---------|-------------------|
| 1 | SCSS Refactor | Clean up styling architecture |
| 2 | Saved Job Descriptions | Edit/save JDs, auto-regenerate resumes |
| 3 | Hiring Projects | Full offer-centric experience with cover letters |
| 4 | AI Profile Enhancement | AI interviews to improve profile entries |

**Recommendation:** Start with **Feature 2: Saved Job Descriptions** - it delivers immediate value, has low risk, and enables Feature 3.

---

*Generated by v3-scope | Architecture Version: 3.0*
