# UX Design: PDF Export

**Date:** 2026-01-03
**Status:** Draft

---

## 1. User Journey

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Resume Preview | Generated resume with edit controls | Reviews/edits resume content | Saved indicator on edit |
| 2 | Resume Preview | "View Mode" toggle (Edit / Preview) | Clicks "Preview" tab | UI switches to clean preview |
| 3 | Preview Mode | Template selector (Classic / Modern) | Selects a template | Resume re-renders in selected template |
| 4 | Preview Mode | "Download PDF" button | Clicks button | Loading state appears |
| 5 | Preview Mode | Download completes | Browser downloads file | Success toast notification |
| 6 | Preview Mode | Downloaded PDF | Opens file | PDF matches preview exactly |

---

## 2. UI States

### View Mode Toggle

Two mutually exclusive modes:
- **Edit Mode**: Current UI with toggle buttons, edit capabilities, section management
- **Preview Mode**: Clean PDF-ready view with template selector

### Template Selector (Preview Mode Only)

- **Condition:** User is in Preview mode
- **Display:** Horizontal tab bar with template names
- **Options:** Classic | Modern
- **Default:** Classic (or last selected, if stored)

### Loading State (PDF Generation)

- **Indicator:** Button text changes to "Generating..." with spinner
- **Location:** Download PDF button
- **Duration:** Typically 1-3 seconds

### Success State

- **Message:** "PDF downloaded"
- **Duration:** 3 seconds auto-dismiss
- **Style:** Toast notification (bottom-right)
- **Next:** User remains on preview, can download again

### Error State

- **Message:** "Could not generate PDF. Please try again."
- **Recovery:** User can click Download again
- **Style:** Toast notification (bottom-right, error color)

---

## 3. Error Messages

| Error | Message | Recovery |
|-------|---------|----------|
| PDF generation failed | "Could not generate PDF. Please try again." | Click Download again |
| Network error | "Connection error. Check your internet and try again." | Check connection, retry |
| Server error | "Something went wrong. Please try again." | Retry |

---

## 4. Wireframes

### Resume Preview - Edit Mode (Current + View Toggle)

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Input                      Match Score: 85%       │
├─────────────────────────────────────────────────────────────┤
│ Senior Software Engineer · Acme Corp                        │
│ Generated Jan 3, 2026                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [ Edit ]  [ Preview ]                                   │ │  ← View mode toggle
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Requirements Analysis                            [−]    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Resume Preview                                              │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ John Doe                                                │ │
│ │ john@email.com · 555-1234                               │ │
│ │ San Francisco, CA · linkedin.com/in/johndoe             │ │
│ │                                                         │ │
│ │ Experienced software engineer with 10+ years...         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Work Experience                              [ON]       │ │  ← Toggle visible
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 1. Senior Engineer · TechCo                             │ │
│ │    Jan 2020 – Present                                   │ │
│ │    Led team of 5 engineers...                           │ │
│ │    Match: Python, AWS                         [Edit]    │ │  ← Edit button visible
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ [ Regenerate ]                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Resume Preview - Preview Mode (PDF Ready)

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Input                      Match Score: 85%       │
├─────────────────────────────────────────────────────────────┤
│ Senior Software Engineer · Acme Corp                        │
│ Generated Jan 3, 2026                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [ Edit ]  [*Preview*]                                   │ │  ← Preview selected
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Template:  [ Classic ]  [ Modern ]        [ Download PDF ]  │  ← Template + download
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │                      JOHN DOE                           │ │
│ │     john@email.com | 555-1234 | San Francisco, CA       │ │
│ │                linkedin.com/in/johndoe                  │ │
│ │                                                         │ │
│ │  ─────────────────────────────────────────────────────  │ │
│ │                                                         │ │
│ │  PROFESSIONAL SUMMARY                                   │ │
│ │  Experienced software engineer with 10+ years of        │ │
│ │  building scalable web applications...                  │ │
│ │                                                         │ │
│ │  ─────────────────────────────────────────────────────  │ │
│ │                                                         │ │
│ │  EXPERIENCE                                             │ │
│ │                                                         │ │
│ │  Senior Engineer | TechCo | Jan 2020 – Present          │ │
│ │  • Led team of 5 engineers building microservices       │ │
│ │  • Reduced deployment time by 40% through CI/CD         │ │
│ │                                                         │ │
│ │  ─────────────────────────────────────────────────────  │ │
│ │                                                         │ │
│ │  SKILLS                                                 │ │
│ │  Python, JavaScript, AWS, Docker, PostgreSQL            │ │
│ │                                                         │ │
│ │  ─────────────────────────────────────────────────────  │ │
│ │                                                         │ │
│ │  EDUCATION                                              │ │
│ │  BS Computer Science | MIT | 2015                       │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                        ↑ This is the PDF preview            │
│                        (same HTML/CSS as PDF output)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Template Options

#### Classic Template

```
┌───────────────────────────────────────────┐
│                                           │
│                JOHN DOE                   │
│   john@email.com | 555-1234 | Location    │
│            linkedin.com/in/jd             │
│                                           │
│ ───────────────────────────────────────── │
│                                           │
│ PROFESSIONAL SUMMARY                      │
│ Brief paragraph about experience...       │
│                                           │
│ ───────────────────────────────────────── │
│                                           │
│ EXPERIENCE                                │
│                                           │
│ Job Title | Company | Dates               │
│ • Achievement 1                           │
│ • Achievement 2                           │
│                                           │
│ ───────────────────────────────────────── │
│                                           │
│ SKILLS                                    │
│ Skill1, Skill2, Skill3, Skill4            │
│                                           │
│ ───────────────────────────────────────── │
│                                           │
│ EDUCATION                                 │
│ Degree | Institution | Year               │
│                                           │
└───────────────────────────────────────────┘

Font: Georgia, Times New Roman (serif)
Header: Centered, uppercase name
Sections: Horizontal rules between sections
```

#### Modern Template

```
┌───────────────────────────────────────────┐
│                                           │
│ JOHN DOE                                  │
│ john@email.com | 555-1234                 │
│ Location | linkedin.com/in/jd             │
│                                           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                           │
│ SUMMARY                                   │
│ Brief paragraph about experience...       │
│                                           │
│ EXPERIENCE                                │
│ ─────────                                 │
│ Job Title                                 │
│ Company | Dates                           │
│ • Achievement 1                           │
│ • Achievement 2                           │
│                                           │
│ SKILLS                                    │
│ ─────────                                 │
│ ┌────────┐ ┌────────┐ ┌────────┐          │
│ │ Skill1 │ │ Skill2 │ │ Skill3 │          │
│ └────────┘ └────────┘ └────────┘          │
│                                           │
│ EDUCATION                                 │
│ ─────────                                 │
│ Degree in Field                           │
│ Institution | Year                        │
│                                           │
└───────────────────────────────────────────┘

Font: Arial, Helvetica (sans-serif)
Header: Left-aligned, bold name
Sections: Underlined headings
Skills: Inline badges/tags style
```

### Mobile Layout (< 768px)

```
┌─────────────────────────┐
│ ← Back         Score: 85│
├─────────────────────────┤
│ Senior Engineer         │
│ Acme Corp               │
│ Jan 3, 2026             │
├─────────────────────────┤
│ [Edit] [Preview]        │
├─────────────────────────┤
│ Template:               │
│ [Classic] [Modern]      │
│                         │
│ [  Download PDF  ]      │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │   PDF Preview       │ │
│ │   (scrollable)      │ │
│ │                     │ │
│ │   ...               │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## 5. Component Specifications

### View Mode Toggle

```
Location: Below title, above Requirements Analysis
Style: Tab bar with underline indicator
States:
  - Edit: Shows current editing UI
  - Preview: Shows clean PDF preview with template selector
```

| Property | Edit Tab | Preview Tab |
|----------|----------|-------------|
| Text | "Edit" | "Preview" |
| Selected style | Border-bottom: 2px solid $color-primary | Same |
| Unselected style | Border-bottom: 2px solid transparent | Same |

### Template Selector

```
Location: Preview mode only, above PDF preview
Style: Pill/tab buttons
Default: "Classic"
```

| Property | Value |
|----------|-------|
| Button padding | 8px 16px |
| Selected background | $color-primary |
| Selected text | #fff |
| Unselected background | transparent |
| Unselected border | 1px solid $color-border |
| Unselected text | $color-text |
| Gap between buttons | 8px |

### Download PDF Button

```
Location: Same row as template selector (right side)
Style: .btn-primary
States:
  - Default: "Download PDF"
  - Loading: "Generating..." (disabled)
  - Success: Toast appears, button returns to default
```

### PDF Preview Container

```
Location: Below template selector in Preview mode
Style:
  - White background
  - Border: 1px solid $color-border
  - Aspect ratio: A4 (210mm x 297mm)
  - Shadow: subtle drop shadow to appear as "paper"
  - Overflow: visible (no scroll within preview)
```

### Success Toast

```
Location: Bottom-right of viewport
Text: "PDF downloaded"
Background: $color-success with 10% opacity
Border: 1px solid $color-success at 30% opacity
Duration: 3 seconds, then fade out
```

---

## 6. Accessibility

- [x] Keyboard navigation: Tab through Edit/Preview toggle, template buttons, Download button
- [x] Focus indicators: 2px solid $color-primary outline on all interactive elements
- [x] Form labels: Template selector buttons have visible labels
- [x] Color contrast: All text meets WCAG 2.1 AA (4.5:1 ratio)
- [x] Screen reader support:
  - View mode toggle: `role="tablist"` with `aria-selected`
  - Template buttons: `role="radiogroup"` with `aria-checked`
  - Loading state: `aria-live="polite"` for status updates
  - Toast: `role="status"` for announcement
- [x] Download button: Clear action text "Download PDF"

---

## 7. PDF Template CSS Requirements

Both templates must use:
- **ATS-friendly fonts:** Arial, Helvetica, Georgia, Times New Roman (no custom fonts)
- **Simple layout:** No CSS columns, no floats for layout, no tables
- **Selectable text:** All content as real text, no images of text
- **Print margins:** 15mm on all sides (for PDF generation)
- **Page size:** A4 (210mm x 297mm)

### Classic Template CSS

```css
.template-classic {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 11pt;
  line-height: 1.4;
}

.template-classic .header {
  text-align: center;
  margin-bottom: 16px;
}

.template-classic .name {
  font-size: 18pt;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.template-classic .section-title {
  font-size: 12pt;
  font-weight: bold;
  text-transform: uppercase;
  border-bottom: 1px solid #000;
  padding-bottom: 4px;
  margin: 16px 0 8px;
}
```

### Modern Template CSS

```css
.template-modern {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 10pt;
  line-height: 1.5;
}

.template-modern .header {
  text-align: left;
  border-bottom: 2px solid #333;
  padding-bottom: 12px;
  margin-bottom: 16px;
}

.template-modern .name {
  font-size: 20pt;
  font-weight: bold;
}

.template-modern .section-title {
  font-size: 11pt;
  font-weight: bold;
  text-transform: uppercase;
  margin: 12px 0 6px;
}

.template-modern .skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.template-modern .skill-tag {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 2px;
  font-size: 9pt;
}
```

---

## 8. API Design

### Endpoint

```
GET /api/resumes/{id}/pdf?template=classic
```

### Parameters

| Parameter | Type | Required | Default | Values |
|-----------|------|----------|---------|--------|
| template | string | No | classic | classic, modern |

### Response

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="John_Doe_Resume_Acme_Corp.pdf"
```

### Filename Format

```
{FullName}_Resume_{CompanyName}.pdf
```

- Spaces replaced with underscores
- Special characters removed
- Example: `John_Doe_Resume_Acme_Corp.pdf`

---

*Next: /v3-verify-analysis*
