# FEATURE_SPEC: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates
**Status:** COMPLETE
**Source:** backlog/done/european-cv-templates.md

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Primary user | A) Job seekers targeting European/Belgian employers | Validated target persona - EU market focus |
| Pain point | A) Current ATS templates don't match European CV expectations | Confirmed need for photo + two-column layouts |
| Assumption: Photo access via personal_info.photo | C) Unsure - needs research | **RESOLVED:** Photo stored in `personal_info.photo` as base64 data URL. Currently excluded from PDF generation (line 31-33 in resume_generator.py). Need to include it for European templates. |
| Assumption: WeasyPrint handles base64 images | C) Unsure - needs testing | **RESEARCHED:** Likely supported (standard HTML), validated in spike |
| Assumption: Two-column layouts work in WeasyPrint | C) Unsure - needs testing | **RESEARCHED:** Use CSS Grid - supports fragmentation between rows |
| Template selector style | UX simplification | Flat dropdown (Template 1-4) instead of grouped selector |

---

## Problem Statement

### User Request (Capability)
Add 2 new CV templates designed for the European/Belgian job market that include profile photo support and European-style layouts.

### Pain Point (Problem)
Current ATS-optimized templates (Classic/Modern) don't match European CV conventions:
- No photo support (standard in EU job applications)
- No two-column layouts (popular in European CVs)
- No dedicated personal details section (nationality, date of birth common in EU)

### User Persona
**European Job Seeker:** A professional targeting jobs in Belgium/EU who needs a CV format that meets local employer expectations, including a professional photo and European layout conventions.

---

## BDD Scenarios

```gherkin
Feature: European CV Templates
  As a job seeker targeting European employers
  I want CV templates with photo support and European layouts
  So that my CV meets local market expectations

  Background:
    Given I have a generated resume
    And I have uploaded a profile photo

  Scenario: Select Brussels Professional template
    Given I am on the resume preview page
    When I select "Template 3" from the template dropdown
    Then I see a two-column layout preview
    And my photo appears in the top-left sidebar
    And my skills appear in the sidebar column

  Scenario: Select EU Classic template
    Given I am on the resume preview page
    When I select "Template 4" from the template dropdown
    Then I see a single-column layout preview
    And my photo appears in the header section
    And sections flow in traditional European format

  Scenario: Download PDF with photo
    Given I have selected the "Brussels Professional" template
    When I click download PDF
    Then the PDF contains my embedded photo
    And the two-column layout is preserved

  Scenario: Template without photo
    Given I have NOT uploaded a profile photo
    When I select the "EU Classic" template
    Then I see a placeholder silhouette in the photo position
    And the layout remains consistent (no collapsed space)

  Scenario: Template dropdown selector
    Given I am on the resume preview page
    When I view the template selector
    Then I see a dropdown with 4 options: Template 1, 2, 3, 4
    And Template 1 corresponds to Classic
    And Template 2 corresponds to Modern
    And Template 3 corresponds to Brussels Professional
    And Template 4 corresponds to EU Classic

  Scenario: Existing templates unchanged
    Given I have a resume
    When I select the "Classic" template
    Then the PDF output is identical to before this feature
    And no photo section is visible
```

---

## Requirements

### Must Have (MVP)

1. **Brussels Professional Template**
   - Two-column layout with left sidebar
   - Photo position: top-left sidebar (circular or rounded)
   - Sidebar: contact info, skills, languages
   - Main column: summary, experience, education, projects
   - Print-optimized CSS with page break handling

2. **EU Classic Template**
   - Single-column traditional layout
   - Photo position: header (right-aligned or centered)
   - Standard European CV section ordering
   - Personal details section support

3. **Photo Integration**
   - Render `personal_info.photo` (base64) in HTML templates
   - Placeholder SVG/initials when no photo uploaded
   - Consistent sizing per template (e.g., 100x100px)

4. **Template Selector Dropdown**
   - Simple dropdown with 4 options: Template 1, 2, 3, 4
   - Replaces current toggle buttons (Classic/Modern)

5. **PDF Generation**
   - Add `brussels` and `eu_classic` to `VALID_TEMPLATES`
   - Pass photo data to template context
   - Handle missing photo gracefully

6. **Frontend Preview**
   - PdfPreview.svelte renders new templates accurately
   - Photo displays in preview matching PDF output

### Should Have

- European date format option (DD/MM/YYYY)
- Optional nationality/DOB fields display

### Won't Have (Out of Scope)

- Photo upload/editing (exists in photo-management)
- Visual skill bars
- Template editor/builder
- Localization (French/Dutch)
- Custom font imports

---

## Technical Assumptions

| Assumption | Category | Status | Notes |
|------------|----------|--------|-------|
| Photo in `personal_info.photo` as base64 data URL | Architecture | **CONFIRMED** | Via routes/photos.py and schemas.py |
| Photo excluded from LLM calls but available in DB | Architecture | **CONFIRMED** | resume_generator.py:31-33 strips it for LLM only |
| WeasyPrint renders base64 images | Library | **RESEARCHED** | Likely works (standard HTML), fallback: temp file |
| Two-column CSS works in WeasyPrint | Library | **RESEARCHED** | Use CSS Grid - supports row fragmentation |
| Existing tests don't rely on template count | Testing | **ASSUMED** | Verify no hardcoded assertions |

---

## Open Questions

1. **Photo sizing:** What dimensions/aspect ratio for photos? (Suggest: 100x100px, circular for Brussels, square for EU Classic)
2. **Placeholder design:** Simple silhouette SVG or initials-based? (Suggest: silhouette for simplicity)
3. **Color scheme:** Match existing blue accent (#0066cc) or different for European templates?

---

## Dependencies

- `photo-management` feature must be complete (provides `personal_info.photo`)

---

## Files Affected

| File | Change Type |
|------|-------------|
| `templates/resume_brussels.html` | CREATE |
| `templates/resume_eu_classic.html` | CREATE |
| `templates/resume_base.css` | MODIFY |
| `services/pdf_generator.py` | MODIFY |
| `routes/resumes.py` | MODIFY (template validation) |
| `src/components/TemplateSelector.svelte` | MODIFY |
| `src/components/PdfPreview.svelte` | MODIFY |

---

*Spec created: 2026-01-08*
