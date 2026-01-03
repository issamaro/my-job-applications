# Change Log: PDF Export

**Date:** 2026-01-03
**Feature Spec:** FEATURE_SPEC_2026-01-03_PDF-EXPORT.md
**Implementation Plan:** IMPL_PLAN_2026-01-03_PDF-EXPORT.md

---

## Files Created

### Backend

| File | Lines | Description |
|------|-------|-------------|
| services/pdf_generator.py | 1-67 | PDF generation service using WeasyPrint + Jinja2 |

### Frontend

| File | Lines | Description |
|------|-------|-------------|
| src/components/PdfPreview.svelte | 1-324 | PDF preview component with HTML resume rendering |
| src/components/TemplateSelector.svelte | 1-56 | Template selector (Classic/Modern) |
| src/components/Toast.svelte | 1-58 | Toast notification component |

### Templates

| File | Lines | Description |
|------|-------|-------------|
| templates/resume_base.css | 1-223 | Shared PDF styling, @page rules, typography |
| templates/resume_classic.html | 1-77 | Classic template (centered, serif fonts) |
| templates/resume_modern.html | 1-81 | Modern template (left-aligned, sans-serif) |

### Tests

| File | Lines | Coverage |
|------|-------|----------|
| tests/test_pdf_export.py | 1-203 | PDF generator unit tests (12 tests) |
| tests/test_pdf_api.py | 1-157 | PDF API endpoint tests (8 tests) |

---

## Files Modified

### Backend

| File | Lines Changed | Change Description |
|------|---------------|-------------------|
| requirements.txt | +2 | Added weasyprint>=62.0, jinja2>=3.1.0 |
| routes/resumes.py | +36 | Added GET /api/resumes/{id}/pdf endpoint |

### Frontend

| File | Lines Changed | Change Description |
|------|---------------|-------------------|
| src/components/ResumePreview.svelte | +71 | View mode toggle, template selector, download button |
| src/lib/api.js | +21 | Added downloadResumePdf() function |
| src/styles/main.scss | +55 | View mode, template selector, toast, PDF preview styles |

---

## Checklist Verification

### Dependencies (CRITICAL)

- [x] weasyprint>=62.0 → requirements.txt:9
- [x] jinja2>=3.1.0 → requirements.txt:10

### WeasyPrint Syntax

- [x] `HTML(string='...')` → services/pdf_generator.py:58
- [x] `CSS(string='...')` → services/pdf_generator.py:59
- [x] `html.write_pdf()` → services/pdf_generator.py:60
- [x] `@page { size: letter; }` → templates/resume_base.css:1

### Jinja2 Syntax

- [x] `Environment(loader=FileSystemLoader(...))` → services/pdf_generator.py:16
- [x] `env.get_template()` → services/pdf_generator.py:51
- [x] `template.render(**context)` → services/pdf_generator.py:56

### FastAPI Syntax

- [x] `Response(content=bytes, media_type='application/pdf')` → routes/resumes.py:101
- [x] Content-Disposition header → routes/resumes.py:102

### Svelte 5 Syntax

- [x] `$state()` for reactive variables → ResumePreview.svelte:14-16
- [x] `onclick={handler}` not `on:click` → ResumePreview.svelte:136-154
- [x] `$props()` for component props → TemplateSelector.svelte:5

### UX Points

- [x] Edit/Preview tab toggle → ResumePreview.svelte:134-154
- [x] Template selector (Classic/Modern) → TemplateSelector.svelte:13-22
- [x] Default template "Classic" → ResumePreview.svelte:15
- [x] Download PDF button → ResumePreview.svelte:167
- [x] Loading state "Generating..." → ResumePreview.svelte:167
- [x] Success toast "PDF downloaded" → ResumePreview.svelte:82
- [x] Error toast "Could not generate PDF..." → ResumePreview.svelte:85
- [x] Toast bottom-right positioning → main.scss:1040

### Accessibility Points

- [x] `role="tablist"` on view toggle → ResumePreview.svelte:134
- [x] `aria-selected` on tabs → ResumePreview.svelte:140,149
- [x] `role="radiogroup"` on template selector → TemplateSelector.svelte:13
- [x] `aria-checked` on template buttons → TemplateSelector.svelte:17
- [x] `role="status"` on toast → Toast.svelte:18
- [x] Focus indicators (outline) → main.scss:1022-1024

### API Points

- [x] GET /api/resumes/{id}/pdf → routes/resumes.py:86
- [x] Query param `template` → routes/resumes.py:87
- [x] Content-Type: application/pdf → routes/resumes.py:101
- [x] Filename format with sanitization → services/pdf_generator.py:30-45

### Content Filtering

- [x] Only `included: true` sections → services/pdf_generator.py:52-53
- [x] Projects default to excluded → Existing resume generator behavior

---

## Test Summary

- Unit Tests: 79 passed
- Integration Tests: via TestClient
- E2E Tests: Manual verification
- New Tests Added: 20 (12 unit + 8 API)

---

## Inspection Summary

- Browser Smoke Test: 6/6 PASS
- Accessibility: 5/5 PASS
- UX Match: 19/19 PASS

---

## Environment Notes

WeasyPrint requires on macOS:
```bash
brew install pango libffi
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
```

---

*Change Log Complete*
