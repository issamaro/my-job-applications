# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2026-01-03] - My Job Applications (Unified View)

### Added
- Expandable resumes inside job items (click to see all resumes for a job)
- Resume linkage: generating from a loaded job links to that job's resumes
- Auto-expand first (most recent) job on page load
- Delete resume from within expanded job item

### Changed
- Renamed "Saved Job Descriptions" to "My Job Applications"
- Consolidated Resume History into Job Applications (one unified view)
- Title auto-updates from "Untitled Job" when generating resume

### Removed
- Separate "History" section (functionality moved to expandable job items)
- ResumeHistory.svelte component
- _history.scss styles (moved to _saved-jobs.scss)

### Technical
- Backend: `job_description_id` parameter in generate endpoint
- Frontend: Expand/collapse toggle with on-demand resume fetching
- 5 new tests for job linkage behavior

---

## [2026-01-03] - SCSS Architecture Refactor

### Changed
- Refactored monolithic `main.scss` (1,047 lines) into 16 focused partials
- Adopted modern Sass module system (`@use`/`@forward` instead of `@import`)
- Centralized design tokens (colors, typography, spacing) in `_tokens.scss`

### Added
- `src/styles/components/` directory with 7 component partials
- `src/styles/views/` directory with 5 view partials
- File header comments describing each partial's purpose
- Index files for component and view directories

### Technical
- Entry point (`main.scss`) reduced to 9 lines of imports
- All partials use `@use "../tokens" as *` for token access
- Import order: tokens → reset → layout → utilities → components → views
- No visual changes (pure code refactor)

---

## [2026-01-03] - PDF Export

### Added
- PDF export functionality with ATS-friendly output
- Two resume templates: Classic (serif, centered) and Modern (sans-serif, left-aligned)
- View mode toggle (Edit/Preview) in resume preview
- Template selector with live preview
- Download PDF button with loading state
- Toast notifications for success/error feedback
- New API endpoint: GET /api/resumes/{id}/pdf?template=classic|modern
- PDF generation service using WeasyPrint + Jinja2
- Comprehensive test coverage (20 new tests)

### Dependencies
- weasyprint >=62.0 (HTML/CSS to PDF)
- jinja2 >=3.1.0 (template rendering)

### Notes
- Requires `export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"` on macOS

---

## [2026-01-03] - Job-Tailored Resume Generation

### Added
- AI-powered resume generation using Claude API
- Job description analysis with requirements extraction
- Match score calculation based on profile vs job requirements
- Tab navigation to switch between Profile and Resume Generator views
- Job description input with 100-character minimum validation
- Progress bar with animated loading states
- Requirements analysis display (required skills, preferred skills, experience, education)
- Toggleable resume sections (work experience, skills, education, projects)
- Inline editing for work experience descriptions
- Resume history with list of previously generated resumes
- Delete confirmation dialog for resume history items
- New API endpoints:
  - POST /api/resumes/generate
  - GET /api/resumes
  - GET /api/resumes/{id}
  - PUT /api/resumes/{id}
  - DELETE /api/resumes/{id}
  - GET /api/profile/complete
- Database tables: job_descriptions, generated_resumes
- Comprehensive test suite (59 tests)

### Dependencies
- anthropic >=0.40.0 (Claude API client)
- python-dotenv >=1.0.0 (environment variable management)

---

## [2026-01-02] - Profile Data Foundation

### Added
- CV profile editor MVP
- Personal information management
- Work experience CRUD
- Education CRUD
- Skills management
- Projects management
- SQLite database persistence
- FastAPI backend with validation
- Svelte 5 frontend with runes

---

*Initial release*
