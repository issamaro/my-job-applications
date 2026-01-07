# Change Log: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language

## Files Modified

### Backend

| File | Changes |
|------|---------|
| `database.py` | Added `languages` table schema with display_order |
| `schemas.py` | Added `CEFRLevel` enum, `Language`, `LanguageCreate`, `LanguageUpdate` schemas |
| `main.py` | Registered languages router |
| `routes/languages.py` | New file - CRUD endpoints for /api/languages |
| `routes/profile_import.py` | Updated to handle languages in profile import |
| `services/profile.py` | Added languages to profile retrieval |
| `services/resume_generator.py` | Include languages in resume content |

### Frontend

| File | Changes |
|------|---------|
| `src/components/Languages.svelte` | New file - Language management component with drag-drop |
| `src/components/ProfileEditor.svelte` | Added Languages section integration |
| `src/components/ResumePreview.svelte` | Added Languages section with toggle |
| `src/components/PdfPreview.svelte` | Updated for languages display |
| `src/lib/api.js` | Added languages API functions |

### Templates

| File | Changes |
|------|---------|
| `templates/resume_classic.html` | Added Languages section |
| `templates/resume_modern.html` | Added Languages section |

### Tests

| File | Changes |
|------|---------|
| `tests/test_languages.py` | New file - 11 tests for language API |

## Checklist Verification

### Syntax Verification (from CHECKLIST)

| Check | File:Line | Status |
|-------|-----------|--------|
| CEFRLevel(str, Enum) | `schemas.py` | ✓ |
| @field_validator | `schemas.py` | ✓ |
| model_validate(dict(row)) | `routes/languages.py` | ✓ |
| APIRouter prefix/tags | `routes/languages.py` | ✓ |
| $state([]) reactive arrays | `Languages.svelte` | ✓ |
| $effect() for mount fetch | `Languages.svelte` | ✓ |
| onclick property | `Languages.svelte` | ✓ |
| ondragstart/ondragover/ondrop | `Languages.svelte` | ✓ |

### UX Verification

| Check | Status |
|-------|--------|
| Empty state message | ✓ |
| Loading skeleton | ✓ |
| Save/Success indicator | ✓ |
| Error messages | ✓ |
| CEFR dropdown with descriptions | ✓ |
| Drag-and-drop reordering | ✓ |
| Delete confirmation | ✓ |
| Resume toggle | ✓ |
| PDF export | ✓ |

## Test Summary

| Metric | Value |
|--------|-------|
| Total Tests | 132 |
| Passed | 131 |
| Failed | 1 (unrelated - test_data_url_too_large) |
| Feature Tests | 11/11 passed |
| Coverage | N/A (pytest-cov not installed) |

## Inspection Summary

| Category | Result |
|----------|--------|
| Browser Smoke Test | ✓ Pass |
| Accessibility (WCAG 2.1 AA) | ✓ Pass |
| UX Match vs Design | ✓ Pass |
| User Verification | 12/12 items pass |
