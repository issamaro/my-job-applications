# Checklist: PDF Export

**Date:** 2026-01-03
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

From LIBRARY_NOTES Section 0:

| Requirement | Version | Verify Command | Status |
|-------------|---------|----------------|--------|
| Python | 3.13 | `python --version` | [ ] |
| Node | 20 | `node --version` | [ ] |
| uv | any | `uv --version` | [ ] |
| nvm | any | `nvm --version` | [ ] |

### System Dependencies (WeasyPrint)

| Dependency | Platform | Install Command | Status |
|------------|----------|-----------------|--------|
| pango | macOS | `brew install pango` | [ ] |
| libffi | macOS | `brew install libffi` | [ ] |

- [ ] Virtual environment activated (`source .venv/bin/activate`)
- [ ] Python dependencies installed (`uv pip install -r requirements.txt`)
- [ ] Node dependencies installed (`npm install`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

From LIBRARY_NOTES - exact version constraints:

| Library | Constraint | File | Status |
|---------|-----------|------|--------|
| weasyprint | `>=62.0` | requirements.txt | [ ] |
| jinja2 | `>=3.1.0` | requirements.txt | [ ] |
| fastapi | `>=0.100.0` | requirements.txt (existing) | [ ] |
| pydantic | `>=2.0` | requirements.txt (existing) | [ ] |
| svelte | `^5.0.0` | package.json (existing) | [ ] |

**STOP if any dependency is missing or has wrong version constraint.**

---

## 2. Syntax Points

From LIBRARY_NOTES - use correct patterns:

### WeasyPrint Syntax

- [ ] Uses `HTML(string='...')` with named parameter → `services/pdf_generator.py`
- [ ] Uses `CSS(string='...')` or `CSS(filename=...)` → `services/pdf_generator.py`
- [ ] Uses `html.write_pdf(stylesheets=[css])` → `services/pdf_generator.py`
- [ ] Page size configured via `@page { size: letter; }` → `templates/resume_base.css`

### Jinja2 Syntax

- [ ] Uses `Environment(loader=FileSystemLoader(...), autoescape=...)` → `services/pdf_generator.py`
- [ ] Uses `env.get_template('name.html')` → `services/pdf_generator.py`
- [ ] Uses `template.render(**context)` → `services/pdf_generator.py`

### FastAPI Syntax

- [ ] Uses `Response(content=bytes, media_type='application/pdf', headers=...)` → `routes/resumes.py`
- [ ] Content-Disposition header format: `attachment; filename="..."` → `routes/resumes.py`

### Pydantic Syntax (v2)

- [ ] Uses `.model_dump()` not `.dict()` → `services/pdf_generator.py`
- [ ] Uses `.model_validate()` if converting from ORM → any new schemas

### Svelte 5 Syntax

- [ ] Uses `$state()` for reactive variables → `ResumePreview.svelte`
- [ ] Uses `$derived()` for computed values (if any) → `ResumePreview.svelte`
- [ ] Uses `onclick={handler}` not `on:click` → all components
- [ ] Uses `$props()` for component props → new components

---

## 3. UX Points

From UX_DESIGN - implement exactly:

### View Mode Toggle

- [ ] Edit/Preview tab toggle visible below title → `ResumePreview.svelte`
- [ ] Edit tab shows current editing UI with toggles → `ResumePreview.svelte`
- [ ] Preview tab shows clean PDF-ready view → `ResumePreview.svelte`
- [ ] Selected tab has `border-bottom: 2px solid $color-primary` → `main.scss`

### Template Selector (Preview Mode Only)

- [ ] Visible only in Preview mode → `ResumePreview.svelte`
- [ ] Two options: "Classic" and "Modern" → `TemplateSelector.svelte`
- [ ] Default: "Classic" → `ResumePreview.svelte`
- [ ] Selected style: `$color-primary` background, white text → `main.scss`
- [ ] Unselected style: transparent background, border → `main.scss`

### Download PDF Button

- [ ] Button text: "Download PDF" (default) → `ResumePreview.svelte`
- [ ] Loading text: "Generating..." with disabled state → `ResumePreview.svelte`
- [ ] Located same row as template selector (right side) → `ResumePreview.svelte`

### Toast Notifications

- [ ] Success message: "PDF downloaded" → `Toast.svelte`
- [ ] Error message: "Could not generate PDF. Please try again." → `Toast.svelte`
- [ ] Location: bottom-right of viewport → `main.scss`
- [ ] Duration: 3 seconds auto-dismiss → `Toast.svelte`
- [ ] Success style: `$color-success` with 10% opacity background → `main.scss`
- [ ] Error style: error color variant → `main.scss`

### PDF Preview Container

- [ ] White background → `main.scss`
- [ ] Border: 1px solid `$color-border` → `main.scss`
- [ ] Shadow: subtle drop shadow (paper appearance) → `main.scss`

---

## 4. PDF Template Points

From UX_DESIGN Section 7:

### ATS-Friendly Requirements

- [ ] Classic template uses Georgia, Times New Roman (serif) → `templates/resume_classic.html`
- [ ] Modern template uses Arial, Helvetica (sans-serif) → `templates/resume_modern.html`
- [ ] No CSS columns for layout → both templates
- [ ] No tables for layout → both templates
- [ ] All text is selectable (no images) → both templates
- [ ] Page margins: 15mm (or 0.75in) → `templates/resume_base.css`

### Classic Template Structure

- [ ] Header: centered, uppercase name → `templates/resume_classic.html`
- [ ] Sections: horizontal rules between → `templates/resume_classic.html`
- [ ] Font size: 11pt body, 18pt name, 12pt section titles → CSS

### Modern Template Structure

- [ ] Header: left-aligned, bold name → `templates/resume_modern.html`
- [ ] Sections: underlined headings → `templates/resume_modern.html`
- [ ] Skills: inline display (tags style) → `templates/resume_modern.html`
- [ ] Font size: 10pt body, 20pt name, 11pt section titles → CSS

---

## 5. API Points

From FEATURE_SPEC and UX_DESIGN:

### Endpoint

- [ ] Route: `GET /api/resumes/{id}/pdf` → `routes/resumes.py`
- [ ] Query param: `template` (optional, default "classic") → `routes/resumes.py`
- [ ] Valid templates: "classic", "modern" → `routes/resumes.py`

### Response

- [ ] Content-Type: `application/pdf` → `routes/resumes.py`
- [ ] Content-Disposition: `attachment; filename="{Name}_Resume_{Company}.pdf"` → `routes/resumes.py`

### Filename Format

- [ ] Format: `{FullName}_Resume_{CompanyName}.pdf` → `services/pdf_generator.py`
- [ ] Spaces replaced with underscores → `services/pdf_generator.py`
- [ ] Special characters removed → `services/pdf_generator.py`

### Error Responses

- [ ] 404 if resume not found → `routes/resumes.py`
- [ ] 400 if invalid template parameter → `routes/resumes.py`
- [ ] 500 if PDF generation fails → `routes/resumes.py`

---

## 6. Content Filtering Points

From FEATURE_SPEC requirements:

- [ ] Only sections with `included: true` appear in PDF → `services/pdf_generator.py`
- [ ] Projects default to `included: false` → `services/pdf_generator.py`
- [ ] Edited descriptions (saved) are used → `services/pdf_generator.py`

---

## 7. Test Points

From FEATURE_SPEC BDD scenarios:

### Unit Tests (`tests/test_pdf_export.py`)

- [ ] Test PDF generation with classic template
- [ ] Test PDF generation with modern template
- [ ] Test filename generation with spaces/special chars
- [ ] Test section filtering (included=true only)
- [ ] Test empty sections handling

### API Tests (`tests/test_pdf_api.py`)

- [ ] Test GET /api/resumes/{id}/pdf returns PDF
- [ ] Test default template is "classic"
- [ ] Test ?template=modern works
- [ ] Test 404 when resume not found
- [ ] Test 400 for invalid template
- [ ] Test Content-Disposition header format

### BDD Scenario Coverage

- [ ] "Export resume with default template" → covered by API tests
- [ ] "Export resume with different template" → covered by API tests
- [ ] "Export resume with excluded sections" → covered by unit tests
- [ ] "PDF is ATS-friendly" → manual verification of template CSS
- [ ] "Export while resume is loading" → frontend disabled state
- [ ] "Export after editing description" → covered by unit tests
- [ ] "No resume to export" → frontend conditional rendering

---

## 8. Accessibility Points

From UX_DESIGN Section 6:

- [ ] View mode toggle: `role="tablist"` with `aria-selected` → `ResumePreview.svelte`
- [ ] Template buttons: `role="radiogroup"` with `aria-checked` → `TemplateSelector.svelte`
- [ ] Loading state: `aria-live="polite"` for status updates → `ResumePreview.svelte`
- [ ] Toast: `role="status"` for announcement → `Toast.svelte`
- [ ] All buttons keyboard accessible (Tab navigation) → all components
- [ ] Focus indicators: 2px solid `$color-primary` outline → `main.scss`
- [ ] Download button: Clear action text "Download PDF" → `ResumePreview.svelte`

---

## 9. Files Created/Modified

### Files to Create

- [ ] `templates/` directory exists
- [ ] `templates/resume_base.css` created
- [ ] `templates/resume_classic.html` created
- [ ] `templates/resume_modern.html` created
- [ ] `services/pdf_generator.py` created
- [ ] `src/components/Toast.svelte` created
- [ ] `src/components/TemplateSelector.svelte` created
- [ ] `src/components/PdfPreview.svelte` created
- [ ] `tests/test_pdf_export.py` created
- [ ] `tests/test_pdf_api.py` created

### Files to Modify

- [ ] `requirements.txt` updated with new dependencies
- [ ] `routes/resumes.py` updated with PDF endpoint
- [ ] `src/components/ResumePreview.svelte` updated with modes/download
- [ ] `src/lib/api.js` updated with downloadResumePdf function
- [ ] `src/styles/main.scss` updated with new styles

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v3-close`.

**Total items:** 94 verification points

---

*Contract for /v3-implement*
