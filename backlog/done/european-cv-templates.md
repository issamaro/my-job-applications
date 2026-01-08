# European CV Templates - SCOPED_FEATURE

**Size:** M (Medium)
**Scoped:** 2026-01-08
**Files affected:** ~6-8
**Dependencies:** `photo-management` (must be implemented first)
**Ready for:** /v5-feature

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Intent type | B) Explore options | Explored template quantity and complexity alternatives |
| Confidence | B) Somewhat confident | Validated assumptions through exploration questions |
| Scope validation | A) Yes, proceed | Reduced from 4 to 2 templates, simplified layouts |
| UX simplification | Flat dropdown | Changed from grouped selector to simple Template 1-4 dropdown |

---

## Description

Add 2 new CV templates designed for the European/Belgian job market. Unlike the existing ATS-optimized templates, these include profile photo support and use two-column or traditional European layouts.

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
- Color usage more common than US/UK markets

---

## Scope (IN)

### A. Templates (2)

1. **Brussels Professional** - Two-column layout, photo top-left, sidebar for skills/contact
2. **EU Classic** - Single-column, photo in header, traditional European format

### B. Technical Deliverables

- [ ] 2 new Jinja2 HTML templates (`templates/resume_{name}.html`)
- [ ] CSS additions to `resume_base.css` for new template classes
- [ ] Photo styling per template (size, shape, border, position)
- [ ] Placeholder image when no photo is provided
- [ ] Update `PdfGeneratorService` to accept new template names
- [ ] Update `TemplateSelector.svelte` with dropdown (Template 1, 2, 3, 4)
- [ ] Update `PdfPreview.svelte` with matching frontend preview styles

### C. Design Characteristics

- Photo integration (using photo from `photo-management`)
- Placeholder silhouette/initials when no photo provided (maintains layout consistency)
- European date format (DD/MM/YYYY)
- Optional personal info fields (nationality, date of birth, etc.)
- Simple, reliable layouts (no visual skill bars or complex elements)
- NOT optimized for ATS parsing (accept text selection issues, non-standard layouts)

---

## Out of Scope (NOT)

- Photo upload/editing (handled by `photo-management` feature)
- Creative Belgian template (visual skill bars - deferred)
- Compact Euro template (dense layout - deferred)
- Removing or modifying existing Classic/Modern templates
- Template editor/builder (custom template creation)
- A/B testing or analytics on template usage
- Localization (French/Dutch text) - templates remain language-agnostic
- Custom font imports (use web-safe fonts for PDF reliability)
- Visual skill bars or complex graphical elements

---

## Success Criteria

- [ ] 2 new templates appear in Template Selector dropdown (Template 3, 4)
- [ ] Each template renders correctly as PDF with embedded photo
- [ ] Photo displays correctly in both frontend preview and PDF output
- [ ] Placeholder shown when no photo is provided (maintains layout)
- [ ] Existing Classic/Modern templates remain unchanged and functional
- [ ] Templates use consistent color schemes and visual hierarchy
- [ ] Two-column layout (Brussels) renders correctly across page breaks

---

## Technical Notes

### Files to Create/Modify

| File | Change |
|------|--------|
| `templates/resume_brussels.html` | NEW - Brussels Professional template |
| `templates/resume_eu_classic.html` | NEW - EU Classic template |
| `templates/resume_base.css` | Add template-specific CSS classes |
| `backend/services/pdf_generator.py` | Add templates to `VALID_TEMPLATES` |
| `frontend/src/components/TemplateSelector.svelte` | Replace toggle buttons with dropdown |
| `frontend/src/components/PdfPreview.svelte` | Add matching preview styles |

### Template Naming Convention

```
resume_brussels.html      → template="brussels"
resume_eu_classic.html    → template="eu_classic"
```

### Photo Integration

- Photo available via `resume.photo` (base64 data URI)
- Embed in template: `<img src="{{ resume.photo }}" />`
- Conditional display: `{% if resume.photo %}...{% else %}<placeholder>{% endif %}`
- Placeholder: SVG silhouette or initials-based placeholder

---

## Suggested Implementation Order

1. **Brussels Professional:** Two-column layout with sidebar (CSS Grid)
2. **EU Classic:** Single-column, simpler structure
3. **Template selector dropdown + preview polish**

---

## Future Expansion (Deferred)

These templates can be added later as separate features:
- **Creative Belgian** - Visual skill bars, accent colors
- **Compact Euro** - Dense information layout

---

*Revised 2026-01-08: Reduced from 4 to 2 templates based on scope exploration. Original scope archived.*
