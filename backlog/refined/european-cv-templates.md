# European CV Templates - SCOPED_FEATURE

**Size:** L (Large)
**Scoped:** 2026-01-04
**Files affected:** ~12-15
**Dependencies:** `photo-management` (must be implemented first)
**Ready for:** /v4-feature

---

## Description

Add 4 new CV templates designed for the European/Belgian job market. Unlike the existing ATS-optimized templates, these prioritize visual appeal, include profile photo support, and use more creative layouts with color.

**Note:** Photo upload/editing functionality is handled by the `photo-management` feature (dependency).

## Context

**Current State:**
- 2 templates exist: Classic (serif, centered) and Modern (sans-serif, left-aligned)
- Both are ATS-friendly (no photos, simple layout, semantic HTML)
- Template system: Jinja2 HTML + CSS → WeasyPrint PDF
- Frontend mirrors backend with Svelte components
- Photo system available (from `photo-management` feature)

**European CV Conventions:**
- Photo placement (typically top-left or top-right)
- Personal details section (nationality, date of birth, etc. - more common in EU)
- Two-column layouts are popular
- More creative/visual designs accepted
- Color usage more common than US/UK markets

---

## Scope (IN)

### A. Templates (4)

1. **Brussels Professional** - Two-column layout, photo top-left, sidebar for skills/contact
2. **EU Classic** - Single-column, photo in header, traditional European format
3. **Creative Belgian** - Modern design, photo with accent color, visual skill bars
4. **Compact Euro** - Dense information layout, small photo, maximizes content per page

### B. Technical Deliverables

- [ ] 4 new Jinja2 HTML templates (`templates/resume_{name}.html`)
- [ ] CSS additions to `resume_base.css` for new template classes
- [ ] Photo styling per template (size, shape, border, position)
- [ ] Update `PdfGeneratorService` to accept new template names
- [ ] Update `TemplateSelector.svelte` with new options (grouped: "ATS-Friendly" / "European Style")
- [ ] Update `PdfPreview.svelte` with matching frontend preview styles
- [ ] Graceful handling when no photo is provided

### C. Design Characteristics

- Photo integration (using photo from `photo-management`)
- European date format (DD/MM/YYYY)
- Optional personal info fields (nationality, date of birth, etc.)
- Color schemes beyond black/blue
- Visual elements (skill bars, icons, borders)
- NOT optimized for ATS parsing (accept text selection issues, non-standard layouts)

---

## Out of Scope (NOT)

- Photo upload/editing (handled by `photo-management` feature)
- Removing or modifying existing Classic/Modern templates
- Template editor/builder (custom template creation)
- A/B testing or analytics on template usage
- Localization (French/Dutch text) - templates remain language-agnostic
- Custom font imports (use web-safe fonts for PDF reliability)

---

## Success Criteria

- [ ] 4 new templates appear in Template Selector, grouped under "European Style"
- [ ] Each template renders correctly as PDF with embedded photo
- [ ] Photo displays correctly in both frontend preview and PDF output
- [ ] Graceful fallback when no photo is provided (placeholder or hidden area)
- [ ] Existing Classic/Modern templates remain unchanged and functional
- [ ] Templates use consistent color schemes and visual hierarchy
- [ ] Two-column layouts render correctly across page breaks

---

## Technical Notes

### Files to Create/Modify

| File | Change |
|------|--------|
| `templates/resume_brussels.html` | NEW - Brussels Professional template |
| `templates/resume_eu_classic.html` | NEW - EU Classic template |
| `templates/resume_creative.html` | NEW - Creative Belgian template |
| `templates/resume_compact_euro.html` | NEW - Compact Euro template |
| `templates/resume_base.css` | Add template-specific CSS classes |
| `backend/services/pdf_generator.py` | Add templates to `VALID_TEMPLATES` |
| `frontend/src/components/TemplateSelector.svelte` | Add new options with grouping |
| `frontend/src/components/PdfPreview.svelte` | Add matching preview styles |

### Template Naming Convention

```
resume_brussels.html      → template="brussels"
resume_eu_classic.html    → template="eu_classic"
resume_creative.html      → template="creative"
resume_compact_euro.html  → template="compact_euro"
```

### Photo Integration

- Photo available via `resume.photo` (base64 data URI)
- Embed in template: `<img src="{{ resume.photo }}" />`
- Conditional display: `{% if resume.photo %}`

---

## Suggested Implementation Order

1. **Brussels Professional:** Most standard two-column layout
2. **EU Classic:** Single-column, simpler structure
3. **Creative Belgian:** More visual elements, skill bars
4. **Compact Euro:** Dense layout optimization
5. **Template selector grouping + preview polish**

---

*Split from original XL feature. Photo management is now separate: `backlog/refined/photo-management.md`*
