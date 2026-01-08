# Change Log: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates

---

## Backend Changes

| File | Lines | Change Type | Description |
|------|-------|-------------|-------------|
| `services/pdf_generator.py` | 12 | MODIFY | Added `brussels`, `eu_classic` to VALID_TEMPLATES |
| `services/pdf_generator.py` | 31-42 | MODIFY | Save/restore photo around LLM call |
| `services/pdf_generator.py` | 75-78 | MODIFY | Added languages to `_prepare_context()` |
| `services/pdf_generator.py` | 207-214 | MODIFY | Fetch current photo from profile in `_row_to_response()` |
| `services/resume_generator.py` | 31-42 | MODIFY | Photo preservation for resume generation |
| `services/resume_generator.py` | 207-214 | MODIFY | Photo fetching for existing resumes |
| `routes/resumes.py` | 77 | MODIFY | Updated template regex pattern |
| `templates/resume_brussels.html` | 1-107 | CREATE | Two-column template with sidebar |
| `templates/resume_eu_classic.html` | 1-93 | CREATE | Single-column EU template with header photo |
| `templates/resume_base.css` | 225-543 | MODIFY | Added CSS for Brussels and EU Classic templates |

## Frontend Changes

| File | Lines | Change Type | Description |
|------|-------|-------------|-------------|
| `src/components/TemplateSelector.svelte` | 1-60 | MODIFY | Replaced buttons with dropdown selector |
| `src/components/PdfPreview.svelte` | 1-835 | MODIFY | Added Brussels/EU Classic template rendering with photo support |

## Test Changes

| File | Lines | Change Type | Description |
|------|-------|-------------|-------------|
| `tests/test_pdf_export.py` | 164-316 | MODIFY | Added 6 tests for new templates |
| `tests/test_pdf_api.py` | 160-181 | MODIFY | Added 2 API tests for new templates |

---

## Checklist Verification

### Section 0: Ecosystem
- [x] Python 3.13 - verified `uv run python --version`
- [x] Jinja2 >=3.1.0 - verified 3.1.6 installed

### Section 2: Syntax/Patterns
- [x] CSS Grid layout - `templates/resume_base.css:243-246`
- [x] `break-inside: avoid` - `templates/resume_base.css:323,342,381,459,478,525`
- [x] Photo conditional - `templates/resume_brussels.html:7-17`
- [x] Photo conditional - `templates/resume_eu_classic.html:19-29`

### Section 3: UX States
- [x] Dropdown with 4 templates - `src/components/TemplateSelector.svelte:4-9`
- [x] Photo placeholder SVG - `src/components/PdfPreview.svelte:38-42`
- [x] Two-column Brussels layout - `src/components/PdfPreview.svelte:32-136`
- [x] Single-column EU Classic - `src/components/PdfPreview.svelte:138-229`

### Section 4: Tests
- [x] `test_generate_pdf_brussels_template` - `tests/test_pdf_export.py:164`
- [x] `test_generate_pdf_eu_classic_template` - `tests/test_pdf_export.py:210`
- [x] `test_generate_pdf_with_photo` - `tests/test_pdf_export.py:256`
- [x] `test_generate_pdf_without_photo_shows_placeholder` - `tests/test_pdf_export.py:278`
- [x] `test_languages_context_included` - `tests/test_pdf_export.py:301`
- [x] `test_export_pdf_brussels_template` - `tests/test_pdf_api.py:160`
- [x] `test_export_pdf_eu_classic_template` - `tests/test_pdf_api.py:172`

### Section 5: Accessibility
- [x] Dropdown has label - `src/components/TemplateSelector.svelte:13`
- [x] Photo has alt text - `templates/resume_brussels.html:8`
- [x] Placeholder has role/aria-label - `templates/resume_brussels.html:10`

---

## Test Summary

| Category | Pass | Fail | Total |
|----------|------|------|-------|
| Unit tests | 138 | 1* | 139 |
| Feature tests | 8 | 0 | 8 |

*Pre-existing failure unrelated to feature (test_data_url_too_large)

---

## Inspection Summary

| Check | Status |
|-------|--------|
| Browser smoke test | PASS |
| Accessibility | PASS |
| UX match | PASS |
| Photo display | PASS (fixed during inspection) |

**Issue Fixed During Inspection:** Photo not displaying - resolved by saving/restoring photo around LLM call and fetching from profile for existing resumes.

---

*Change log created: 2026-01-08*
