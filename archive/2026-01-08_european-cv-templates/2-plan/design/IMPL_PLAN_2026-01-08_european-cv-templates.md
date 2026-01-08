# Implementation Plan: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates
**Status:** DRAFT

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| UI Approach | A) Replace with dropdown | Use native HTML select instead of toggle buttons |
| Plan review | A) Looks good - proceed | No changes needed, proceed to checklist |

---

## 1. Affected Files Analysis

### Config/Dependencies

| File | Change Type | Description |
|------|-------------|-------------|
| None | - | No new dependencies required; using existing WeasyPrint >=62.0 |

### Backend

| File | Change Type | Description |
|------|-------------|-------------|
| `services/pdf_generator.py` | MODIFY | Add `brussels`, `eu_classic` to VALID_TEMPLATES |
| `routes/resumes.py` | MODIFY | Update template regex pattern |
| `templates/resume_brussels.html` | CREATE | Two-column template with photo sidebar |
| `templates/resume_eu_classic.html` | CREATE | Single-column template with header photo |
| `templates/resume_base.css` | MODIFY | Add CSS for new templates (CSS Grid, photo styles) |

### Frontend

| File | Change Type | Description |
|------|-------------|-------------|
| `src/components/TemplateSelector.svelte` | MODIFY | Replace buttons with dropdown selector |
| `src/components/PdfPreview.svelte` | MODIFY | Add template-specific rendering + photo display |

### Tests

| File | Change Type | Description |
|------|-------------|-------------|
| `tests/test_pdf_export.py` | MODIFY | Add tests for new templates |
| `tests/test_pdf_api.py` | MODIFY | Add API tests for new template validation |

---

## 2. Database Changes

**None required.**

Photo already stored in `personal_info.photo` as base64 data URI (via photo-management feature).

---

## 3. Implementation Approach

### Selected Approach: Dropdown UI

Replace toggle buttons with a native HTML `<select>` dropdown. This approach:
- Scales cleanly to 4 templates
- Matches UX_DESIGN specification
- Reduces horizontal space usage
- Simpler to maintain

### Service Pattern

Follow existing pattern in `pdf_generator.py`:
- Template files named `resume_{template_name}.html`
- Validation via `VALID_TEMPLATES` list
- Context passed via `_prepare_context()` (already includes `personal_info.photo`)

### Validation Approach

- **Backend:** FastAPI Query regex pattern: `^(classic|modern|brussels|eu_classic)$`
- **Service:** `VALID_TEMPLATES = ["classic", "modern", "brussels", "eu_classic"]`
- **Frontend:** Hardcoded template options array

### Error Handling

- Missing photo: Display SVG placeholder (no error, graceful degradation)
- Invalid template: Return HTTP 400 (existing behavior)
- Template render failure: Return HTTP 500 with error message

### CSS Strategy

Use CSS Grid for two-column layout (per LIBRARY_NOTES research):
```css
.template-brussels {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 24px;
}
```

Page breaks: `break-inside: avoid` on sections (existing pattern).

---

## 4. Implementation Order

### Step 0: Backend Configuration
1. `services/pdf_generator.py:18` - Add templates to VALID_TEMPLATES list

### Step 1: Backend Route
2. `routes/resumes.py:78` - Update template regex pattern

### Step 2: Backend Templates (CSS First)
3. `templates/resume_base.css` - Add `.template-brussels` and `.template-eu_classic` CSS classes
4. `templates/resume_brussels.html` - CREATE two-column template
5. `templates/resume_eu_classic.html` - CREATE single-column template

### Step 3: Frontend Components
6. `src/components/TemplateSelector.svelte` - Replace buttons with dropdown
7. `src/components/PdfPreview.svelte` - Add template-specific rendering + photo

### Step 4: Tests
8. `tests/test_pdf_export.py` - Add unit tests for new templates
9. `tests/test_pdf_api.py` - Add API endpoint tests

---

## 5. Detailed Implementation Steps

### Step 0.1: Update VALID_TEMPLATES
**File:** `services/pdf_generator.py`
**Line:** 18
**Change:** Add new template names
```python
# Before
VALID_TEMPLATES = ["classic", "modern"]

# After
VALID_TEMPLATES = ["classic", "modern", "brussels", "eu_classic"]
```

### Step 1.1: Update Route Validation
**File:** `routes/resumes.py`
**Line:** 78
**Change:** Update regex pattern
```python
# Before
template: str = Query(default="classic", pattern="^(classic|modern)$")

# After
template: str = Query(default="classic", pattern="^(classic|modern|brussels|eu_classic)$")
```

### Step 2.1: Add CSS Classes
**File:** `templates/resume_base.css`
**Location:** After line 223 (end of .template-modern)
**Add:** ~100 lines of new CSS

Key classes:
- `.template-brussels` - CSS Grid two-column layout
- `.template-eu_classic` - Single-column European layout
- `.profile-photo` - Photo sizing (100x100px)
- `.photo-placeholder` - Gray silhouette SVG container
- `.sidebar` - Left column styles for Brussels template

### Step 2.2: Create Brussels Template
**File:** `templates/resume_brussels.html` (CREATE)
**Structure:**
```
<div class="template-brussels">
  <aside class="sidebar">
    {% if personal_info.photo %}
      <img src="{{ personal_info.photo }}" class="profile-photo circular">
    {% else %}
      <div class="photo-placeholder circular"><!-- SVG silhouette --></div>
    {% endif %}
    <section class="contact">...</section>
    <section class="skills">...</section>
    <section class="languages">...</section>
  </aside>
  <main class="main-content">
    <h1>{{ personal_info.full_name }}</h1>
    <section class="summary">...</section>
    <section class="experience">...</section>
    <section class="education">...</section>
    <section class="projects">...</section>
  </main>
</div>
```

### Step 2.3: Create EU Classic Template
**File:** `templates/resume_eu_classic.html` (CREATE)
**Structure:**
```
<div class="template-eu_classic">
  <header class="cv-header">
    <div class="header-content">
      <h1>{{ personal_info.full_name }}</h1>
      <div class="contact">...</div>
    </div>
    {% if personal_info.photo %}
      <img src="{{ personal_info.photo }}" class="profile-photo square">
    {% else %}
      <div class="photo-placeholder square"><!-- SVG silhouette --></div>
    {% endif %}
  </header>
  <section class="summary">...</section>
  <section class="experience">...</section>
  <section class="education">...</section>
  <section class="skills">...</section>
  <section class="languages">...</section>
  <section class="projects">...</section>
</div>
```

### Step 3.1: Update Template Selector
**File:** `src/components/TemplateSelector.svelte`
**Change:** Replace button grid with dropdown

```svelte
<script>
  let { selected = $bindable('classic') } = $props();

  const templates = [
    { id: 'classic', name: 'Template 1' },
    { id: 'modern', name: 'Template 2' },
    { id: 'brussels', name: 'Template 3' },
    { id: 'eu_classic', name: 'Template 4' }
  ];
</script>

<select bind:value={selected} class="template-dropdown">
  {#each templates as template}
    <option value={template.id}>{template.name}</option>
  {/each}
</select>
```

### Step 3.2: Update PDF Preview
**File:** `src/components/PdfPreview.svelte`
**Changes:**
1. Add photo rendering for European templates
2. Add template-specific layouts for `brussels` and `eu_classic`
3. Add placeholder SVG component

Key additions:
- Photo display: `{#if resumeData.personal_info?.photo && (template === 'brussels' || template === 'eu_classic')}`
- Two-column layout for Brussels template
- Header photo for EU Classic template
- Placeholder SVG inline (no external file dependency)

### Step 4.1: Unit Tests
**File:** `tests/test_pdf_export.py`
**Add tests:**
- `test_generate_pdf_brussels_template()`
- `test_generate_pdf_eu_classic_template()`
- `test_generate_pdf_with_photo()`
- `test_generate_pdf_without_photo_shows_placeholder()`

### Step 4.2: API Tests
**File:** `tests/test_pdf_api.py`
**Add tests:**
- `test_export_pdf_brussels_template()`
- `test_export_pdf_eu_classic_template()`
- `test_export_pdf_invalid_template_returns_400()`

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Base64 images fail in WeasyPrint | LOW | HIGH | Fallback: save to temp file, reference by path |
| CSS Grid breaks on page boundaries | LOW | MEDIUM | Test with long CVs; use `break-inside: avoid` |
| Frontend preview doesn't match PDF | MEDIUM | MEDIUM | Use same CSS classes; test side-by-side |
| Photo aspect ratio distortion | LOW | LOW | Use `object-fit: cover` with fixed dimensions |
| Existing tests break | LOW | LOW | Run test suite before/after; no hardcoded template counts found |

---

## 7. Implementation Notes

### Photo Placeholder SVG

Inline SVG silhouette (avoid external file):
```html
<svg viewBox="0 0 100 100" class="silhouette">
  <circle cx="50" cy="35" r="20" fill="#9CA3AF"/>
  <ellipse cx="50" cy="85" rx="35" ry="25" fill="#9CA3AF"/>
</svg>
```

### CSS Variables (for consistency)

```css
:root {
  --eu-photo-size: 100px;
  --eu-sidebar-width: 180px;
  --eu-accent-color: #0066cc;
  --eu-placeholder-bg: #F3F4F6;
  --eu-placeholder-fg: #9CA3AF;
}
```

### Page Size Consideration

Existing templates use US Letter. European templates should ideally use A4:
```css
@page {
  size: A4;  /* 210mm x 297mm */
  margin: 20mm;
}
```

This will be template-specific (Brussels/EU Classic use A4, Classic/Modern keep Letter).

---

## 8. Dependencies

| Dependency | Status |
|------------|--------|
| photo-management feature | COMPLETE (provides personal_info.photo) |
| WeasyPrint >=62.0 | INSTALLED (no changes needed) |
| Jinja2 >=3.1.0 | INSTALLED (no changes needed) |

---

## 9. Summary

| Category | Count |
|----------|-------|
| Files to create | 2 |
| Files to modify | 7 |
| New CSS classes | ~10 |
| New tests | 4-6 |

**Estimated complexity:** Medium - follows existing patterns, no new dependencies.

---

*Implementation Plan created: 2026-01-08*
