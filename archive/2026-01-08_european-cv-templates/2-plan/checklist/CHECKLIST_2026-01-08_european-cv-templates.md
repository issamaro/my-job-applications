# Verification Checklist: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates
**Status:** DRAFT

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Checklist review | A) Looks complete | No changes needed, proceed to verification |

---

## Section 0: Ecosystem

| Component | Required | Verify Command |
|-----------|----------|----------------|
| Python | 3.13 | `python --version` |
| Virtual environment | Active | `which python` shows `.venv` path |
| WeasyPrint | >=62.0 | `python -c "import weasyprint; print(weasyprint.__version__)"` |
| Jinja2 | >=3.1.0 | `python -c "import jinja2; print(jinja2.__version__)"` |
| Node.js | (frontend) | `node --version` |

### Ecosystem Checklist

- [ ] Python 3.13 installed and active
- [ ] Virtual environment activated (`.venv`)
- [ ] All backend dependencies installed (`uv sync`)
- [ ] Frontend dependencies installed (`npm install` in project root)

---

## Section 1: Dependencies

| Library | Constraint | Manifest | Status |
|---------|------------|----------|--------|
| WeasyPrint | >=62.0 | `pyproject.toml` | Already installed |
| Jinja2 | >=3.1.0 | `pyproject.toml` | Already installed |

### Dependency Checklist

- [ ] No new dependencies required (confirm `pyproject.toml` unchanged)
- [ ] Existing WeasyPrint version supports CSS Grid (`>=62.0`)

---

## Section 2: Syntax/Patterns

### CSS Grid Layout (from LIBRARY_NOTES)

- [ ] Use `display: grid` (not flexbox) for two-column layout → `templates/resume_base.css`
- [ ] Use `grid-template-columns: 180px 1fr` for sidebar width → `templates/resume_base.css`
- [ ] Apply `break-inside: avoid` to sections → `templates/resume_base.css`
- [ ] Avoid `display: inline-grid` (not supported) → `templates/resume_base.css`

### Jinja2 Templates (existing pattern)

- [ ] Template naming: `resume_{template_name}.html` → `templates/`
- [ ] Photo conditional: `{% if personal_info.photo %}` → `templates/resume_brussels.html`
- [ ] Photo conditional: `{% if personal_info.photo %}` → `templates/resume_eu_classic.html`
- [ ] Section loops: `{% for exp in work_experiences %}` → both new templates

### WeasyPrint Page Setup

- [ ] A4 page size for European templates: `@page { size: A4; }` → `templates/resume_base.css`
- [ ] Appropriate margins: `margin: 20mm` → `templates/resume_base.css`

---

## Section 3: UX States

### Template Selector States (from UX_DESIGN)

- [ ] Closed state: Shows selected template name + chevron → `src/components/TemplateSelector.svelte`
- [ ] Open state: Flat list of 4 templates visible → `src/components/TemplateSelector.svelte`
- [ ] Loading state: Spinner during template switch → `src/components/PdfPreview.svelte`

### Preview States (from UX_DESIGN)

- [ ] Loading state: Skeleton/shimmer while fetching → `src/components/PdfPreview.svelte`
- [ ] Loaded with photo: CV displays embedded photo → `src/components/PdfPreview.svelte`
- [ ] Loaded without photo: CV displays placeholder silhouette → `src/components/PdfPreview.svelte`
- [ ] Download in progress: Button shows spinner → `src/components/ResumePreview.svelte`

### Photo States (from UX_DESIGN)

- [ ] Placeholder: Gray silhouette 100x100px → `templates/resume_base.css`
- [ ] Placeholder hover: "Add Photo" tooltip → `src/components/PdfPreview.svelte`
- [ ] Photo loaded: Square photo with CSS border-radius → `templates/resume_base.css`

### Error Messages (from UX_DESIGN)

- [ ] Template load failed: "Couldn't load template. Please try again." → `src/components/PdfPreview.svelte`
- [ ] PDF generation failed: "PDF generation failed. Please try again." → `src/components/ResumePreview.svelte`

---

## Section 4: Tests

### Unit Tests (from IMPL_PLAN)

- [ ] `test_generate_pdf_brussels_template()` → `tests/test_pdf_export.py`
- [ ] `test_generate_pdf_eu_classic_template()` → `tests/test_pdf_export.py`
- [ ] `test_generate_pdf_with_photo()` → `tests/test_pdf_export.py`
- [ ] `test_generate_pdf_without_photo_shows_placeholder()` → `tests/test_pdf_export.py`

### API Tests (from IMPL_PLAN)

- [ ] `test_export_pdf_brussels_template()` → `tests/test_pdf_api.py`
- [ ] `test_export_pdf_eu_classic_template()` → `tests/test_pdf_api.py`
- [ ] `test_export_pdf_invalid_template_returns_400()` (verify existing test still passes) → `tests/test_pdf_api.py`

### Regression Tests

- [ ] Existing Classic template generates identical PDF → `tests/test_pdf_export.py`
- [ ] Existing Modern template generates identical PDF → `tests/test_pdf_export.py`
- [ ] All existing tests pass (`pytest tests/`)

---

## Section 5: Accessibility

### Keyboard Navigation (from UX_DESIGN)

- [ ] Dropdown opens with Enter/Space → `src/components/TemplateSelector.svelte`
- [ ] Arrow keys navigate dropdown options → `src/components/TemplateSelector.svelte`
- [ ] Escape closes dropdown → `src/components/TemplateSelector.svelte`
- [ ] Tab moves focus to next element → `src/components/TemplateSelector.svelte`

### Focus Indicators (from UX_DESIGN)

- [ ] Visible focus state (blue outline) on dropdown → `src/components/TemplateSelector.svelte`
- [ ] Focus ring on download button → `src/components/ResumePreview.svelte`

### Labels and Semantics

- [ ] Dropdown has accessible label (`aria-label` or `<label>`) → `src/components/TemplateSelector.svelte`
- [ ] Photo has alt text: `alt="Profile photo"` → `templates/resume_brussels.html`
- [ ] Photo has alt text: `alt="Profile photo"` → `templates/resume_eu_classic.html`
- [ ] Placeholder has `role="img"` and `aria-label` → both templates

### Contrast (from UX_DESIGN)

- [ ] Text meets WCAG 2.1 AA (4.5:1 ratio) → `templates/resume_base.css`
- [ ] Placeholder gray (#9CA3AF) on background (#F3F4F6) meets 3:1 → `templates/resume_base.css`

---

## Section 6: Project-Specific

None - no `project-checks.md` found.

---

## Summary

| Section | Check Count |
|---------|-------------|
| 0. Ecosystem | 4 |
| 1. Dependencies | 2 |
| 2. Syntax/Patterns | 10 |
| 3. UX States | 12 |
| 4. Tests | 10 |
| 5. Accessibility | 11 |
| 6. Project-Specific | 0 |
| **Total** | **49** |

---

*Checklist created: 2026-01-08*
