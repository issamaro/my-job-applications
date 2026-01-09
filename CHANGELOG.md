# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2026-01-09] - Job Requirements Analysis Persistence Fix

### Fixed
- Job Requirements Analysis section now persists after page refresh
- Fixed UPDATE queries in resume_generator.py to save `parsed_data`
- Both UPDATE branches (title update + timestamp only) now include job analysis

### Added
- 2 new tests for job analysis persistence with existing job descriptions

### Technical
- Root cause: UPDATE queries were missing `parsed_data` parameter
- INSERT path worked correctly; UPDATE paths did not save job analysis
- Fix adds `json.dumps(llm_result.get("job_analysis", {}))` to both UPDATE branches

---

## [2026-01-09] - SCSS to CSS Custom Properties Migration

### Changed
- Migrated from SCSS to CSS Custom Properties (CSS variables)
- Replaced 20 SCSS files with single `global.css` + Svelte scoped styles
- Simplified build scripts from 4 to 2 (`build`, `dev`)
- Removed sass dependency from project

### Added
- `src/styles/global.css` with CSS Custom Properties for design tokens
- RGB color variants (`--color-*-rgb`) for alpha transparency support
- Scoped `<style>` blocks in 14 Svelte components
- CSS native nesting for cleaner style organization

### Removed
- sass package dependency
- `build:css` and `watch:css` npm scripts
- 20 SCSS files (tokens, reset, layout, utilities, components, views)
- `src/styles/components/` and `src/styles/views/` directories

### Technical
- Build time unchanged (~1.1s)
- Bundle size: 48KB CSS, 141KB JS
- No visual changes (pure refactoring)
- Enables future dark mode implementation

---

## [2026-01-08] - Multi-Language Resume Generation

### Added
- Language selector in Resume Generator (English, French, Dutch)
- Resume generation in selected language via LLM instructions
- Translated section headers in PDF preview (Expérience, Compétences, etc.)
- Translated section headers in PDF export
- Language badge showing selected language on resume preview
- Localized date formatting (month names, "Present" label)
- Translation files for en/fr/nl (`translations/*.json`)
- New translation service (`services/translations.py`)
- LanguageSelector component (`src/components/LanguageSelector.svelte`)
- 39 new tests for language functionality

### Changed
- API: `POST /api/resumes/generate` accepts `language` parameter
- API: `GET /api/resumes/{id}/pdf` accepts `language` parameter
- Resume response includes `language` field
- PDF templates use translation variables instead of hardcoded English

### Technical
- Language stored per-resume in database
- Jinja2 templates receive translations via context
- Frontend uses derived translations based on resume.language

---

## [2026-01-06] - Claude Code Configuration Cleanup

### Changed
- Removed legacy `venv/` Python path permission from Claude Code settings
- Only `.venv/` is now permitted as the canonical Python environment

### Added
- Python Environment section in `.claude/readme.md`
- Documentation explaining canonical path and `uv` workflow

### Technical
- Defensive change to prevent interpreter ambiguity
- Aligns with modern `uv` tooling (`uv sync`, `uv run`)

---

## [2026-01-05] - Import JSON Profile

### Added
- Import JSON button in Profile Editor
- ImportModal component with drag-drop file upload
- Frontend JSON validation (syntax, schema, required fields)
- Preview state showing item counts before import
- Sample JSON download for schema reference
- PUT /api/profile/import endpoint with atomic transaction
- 9 new tests for import functionality

### Technical
- Two-layer validation (frontend + backend Pydantic)
- Atomic clear+insert preserving profile photo
- Full accessibility support (ARIA, keyboard navigation)
- SASS styles using design tokens

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
