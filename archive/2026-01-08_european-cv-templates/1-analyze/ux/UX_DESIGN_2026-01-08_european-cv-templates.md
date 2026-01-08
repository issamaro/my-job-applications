# UX Design: European CV Templates

**Date:** 2026-01-08
**Feature:** european-cv-templates
**Status:** DRAFT

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Current state | User described - Toggle buttons (Classic/Modern), no grouping, no photo | Understood baseline |
| Preserve/rethink | Redesign welcome | Replace toggle buttons with dropdown |
| State review | Simplified per user feedback | Flat list, no groups |
| Additional constraints | No mobile, square photos only | Removed mobile wireframes, unified photo size |

---

## 1. User Journey

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Preview page | Dropdown showing current template | Clicks dropdown | Flat list of 4 templates appears |
| 2 | Dropdown | Template 1, 2, 3, 4 | Clicks "Template 3" | Dropdown closes, preview updates |
| 3 | Preview area | Two-column layout with photo placeholder | Views preview | Sees placeholder silhouette |
| 4 | Preview area | Placeholder with "Add Photo" on hover | Navigates to Profile | Uploads photo there |
| 5 | Preview (with photo) | CV with actual photo | Reviews layout | Photo appears in position |
| 6 | Action bar | "Download PDF" button | Clicks download | PDF downloads |

---

## 2. State Definitions

### Template Selector States

| State | Condition | User Sees | User Can Do |
|-------|-----------|-----------|-------------|
| Closed | Default | Selected template name + chevron | Click to open |
| Open | User clicked | Flat list of 4 templates | Select template |
| Loading | Template switching | Spinner | Wait |

### Preview States

| State | Condition | User Sees | User Can Do |
|-------|-----------|-----------|-------------|
| Loading | Fetching template | Skeleton/shimmer | Wait |
| Loaded - With Photo | Photo data exists | CV with embedded photo | Download |
| Loaded - No Photo | No photo uploaded | CV with placeholder silhouette | Navigate to Profile to add |
| Download In Progress | User clicked download | Button shows spinner | Wait |
| Download Error | Generation failed | Toast: "Download failed. Try again." | Retry |

### Photo States

| State | Condition | User Sees | User Can Do |
|-------|-----------|-----------|-------------|
| Placeholder | No photo | Gray silhouette (100x100px square) | Hover shows tooltip |
| Photo Loaded | Photo exists | Square photo (CSS crops to circle if needed) | View |

---

## 3. Error Messages

| Error Type | User Message | Recovery Action |
|------------|--------------|-----------------|
| Template load failed | "Couldn't load template. Please try again." | Retry |
| PDF generation failed | "PDF generation failed. Please try again." | Click Download PDF again |

---

## 4. Wireframes

### Current UI (Reference)

```
+------------------------------------------------------------------+
| MyCV                                Profile    Resume Generator   |
+------------------------------------------------------------------+
| <- Back to Input                                   Match Score: 79%|
| Software Developer · Odoo                                         |
| Generated Jan 7, 2026                                             |
+------------------------------------------------------------------+
|                                                                    |
|   Edit    Preview          [Classic] [Modern]    [Download PDF]   |
|           -------                                                  |
+------------------------------------------------------------------+
|                                                                    |
|                         CV PREVIEW                                 |
|                     (single column)                                |
|                                                                    |
+------------------------------------------------------------------+
```

### Redesigned UI - Desktop

```
+------------------------------------------------------------------+
| MyCV                                Profile    Resume Generator   |
+------------------------------------------------------------------+
| <- Back to Input                                   Match Score: 79%|
| Software Developer · Odoo                                         |
| Generated Jan 7, 2026                                             |
+------------------------------------------------------------------+
|                                                                    |
|   Edit    Preview          [v Template 3    ]    [Download PDF]   |
|           -------          +-----------------+                    |
|                            | Template 1      |                    |
|                            | Template 2      |                    |
|                            | Template 3  [x] |  <- selected       |
|                            | Template 4      |                    |
|                            +-----------------+                    |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+----------------------------------------+    |
|  |  +----------+    |                                        |    |
|  |  |  PHOTO   |    |           AÏSSA CASA                   |    |
|  |  | 100x100  |    |    aissacasapro@gmail.com | +324...    |    |
|  |  +----------+    |                                        |    |
|  |  Contact         |        PROFESSIONAL SUMMARY            |    |
|  |  Skills          |        ...                             |    |
|  |  Languages       |                                        |    |
|  |                  |        EXPERIENCE                      |    |
|  |                  |        ...                             |    |
|  +------------------+----------------------------------------+    |
|                      (Two-column European template)               |
+------------------------------------------------------------------+
```

### Template Dropdown - Simple List

```
+-----------------+
| v Template 3    |  <- Shows selected
+-----------------+
| Template 1      |  Classic (ATS)
| Template 2      |  Modern (ATS)
| Template 3  [x] |  Brussels Professional (EU) - selected
| Template 4      |  EU Classic (EU)
+-----------------+
```

### Photo Placeholder

```
+----------+
|   ____   |
|  /    \  |
| |      | |
|  \____/  |
+----------+
  100x100px
  square base

CSS border-radius: 50% for circular display (Brussels)
CSS border-radius: 4px for square display (EU Classic)
```

---

## 5. Component Specifications

### Template Selector Dropdown

- **Width:** 180px
- **Options:** Template 1, Template 2, Template 3, Template 4
- **Active indicator:** Checkmark on selected item

### Photo Display

| Property | Value |
|----------|-------|
| Base size | 100x100px (square) |
| Brussels Professional | `border-radius: 50%` (circular) |
| EU Classic | `border-radius: 4px` (rounded square) |
| Position (Brussels) | Top-left sidebar |
| Position (EU Classic) | Header, right-aligned |

### Placeholder Silhouette

- **Size:** 100x100px square
- **Color:** #9CA3AF (gray-400)
- **Background:** #F3F4F6 (gray-100)
- **Hover:** "Add Photo" tooltip

---

## 6. Accessibility Checklist

- [x] All interactive elements keyboard accessible
- [x] Focus states visible (blue outline)
- [x] Dropdown has accessible label
- [x] Color contrast meets WCAG 2.1 AA
- [x] Error states announced to screen readers
- [x] Escape key closes dropdown
- [x] Arrow keys navigate dropdown options

---

## 7. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dropdown vs buttons | Dropdown | Scales to 4 templates cleanly |
| Grouping | None (flat list) | Simpler, user preference |
| Naming | Template 1-4 | Generic, simple |
| Photo size | 100x100px square | Single size works for both circular and square display |
| Mobile | Not supported | App is desktop-only |

---

*UX Design created: 2026-01-08*
*Next: /v5-verify-analysis*
