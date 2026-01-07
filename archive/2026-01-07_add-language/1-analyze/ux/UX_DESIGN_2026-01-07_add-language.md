# UX Design: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language
**Source:** `workbench/1-analyze/requirements/FEATURE_SPEC_2026-01-07_add-language.md`

## User Journey

### Profile Page - Managing Languages

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Profile > Languages | Section header with "+" button | Clicks "+" to add | Form appears |
| 2 | Add form | Name input + CEFR dropdown | Enters "French", selects "B2" | Real-time validation |
| 3 | Save | Save/Cancel buttons | Clicks "Save" | "Saving..." then "Saved" indicator |
| 4 | List view | Language items in list | Views entries | Items shown with drag handles |
| 5 | Reorder | Drag handles on items | Drags item to new position | Visual feedback, order persists |
| 6 | Edit | Edit button on item | Clicks "Edit" | Form populates with data |
| 7 | Delete | Delete link in edit form | Clicks "Delete" | Confirmation dialog |

### Resume Preview - Viewing Languages

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Resume Preview | Languages section with toggle | Views languages | Shows "French - B2" format |
| 2 | Toggle off | [ON]/[OFF] button | Clicks toggle | Section shows "(Section hidden)" |
| 3 | PDF Export | Download button | Clicks "Download PDF" | PDF includes languages section |

## State Definitions

| State | Condition | User Sees | User Can Do |
|-------|-----------|-----------|-------------|
| Empty | No languages in database | "No languages added yet." + visible section | Click "+" to add first |
| Loading | Data fetching on mount | Skeleton placeholder | Wait |
| Loaded | Languages retrieved | List of language items with drag handles | View, drag to reorder, click Edit |
| Form (Add) | "+" clicked | Empty form with Name input + CEFR dropdown | Enter data, Save, Cancel |
| Form (Edit) | Edit clicked on item | Pre-filled form | Modify data, Save, Cancel, Delete |
| Saving | Save in progress | "Saving..." on button | Wait |
| Success | Save completed | "Saved" indicator (fades after 2s) | Continue |
| Error | Operation failed | "Could not save/delete. Please try again." | Retry |
| Delete Confirm | Delete clicked | ConfirmDialog: "Delete this language?" | Confirm or Cancel |

## Component Structure

```
ProfileEditor.svelte
├── Section title="Languages" onAdd={() => languagesRef?.add()}
│   └── Languages.svelte (new component)
│       ├── Loading: skeleton
│       ├── Error: error message
│       ├── Empty: empty-state message
│       ├── List: draggable items
│       │   └── Language item (name - level) with Edit button
│       ├── Add/Edit Form
│       │   ├── Name input (required)
│       │   ├── CEFR level select (A1-C2)
│       │   └── Save/Cancel/Delete buttons
│       └── ConfirmDialog (for delete)

ResumePreview.svelte
├── ResumeSection title="Languages" (with toggle)
│   └── Language list display
│       └── "French - B2" format (code only, no descriptions)
```

## Error Messages

| Error Type | User Message | Recovery |
|------------|--------------|----------|
| Load failed | "Could not load profile. Please refresh." | Refresh page |
| Save failed | "Could not save. Please try again." | Retry save |
| Delete failed | "Could not delete. Please try again." | Retry delete |
| Validation - Name | "Required" (inline) | Enter language name |
| Validation - Level | "Required" (inline) | Select CEFR level |
| API - Invalid level | "Invalid CEFR level" | Select valid A1-C2 |

## Wireframes

### Profile Page - Languages Section

```
Mobile (< 768px):                    Desktop (>= 768px):
+------------------------+           +------------------------------------------+
|  Languages          [+]|           |  Languages                            [+]|
+------------------------+           +------------------------------------------+
|  ⋮⋮ English - C2  [Edit]|           |  ⋮⋮ English - C2                   [Edit]|
|  ⋮⋮ French - B2   [Edit]|           |  ⋮⋮ French - B2                    [Edit]|
|  ⋮⋮ Spanish - A2  [Edit]|           |  ⋮⋮ Spanish - A2                   [Edit]|
+------------------------+           +------------------------------------------+
```

### Add/Edit Form

```
Mobile (< 768px):                    Desktop (>= 768px):
+------------------------+           +------------------------------------------+
| Language *             |           | Language *        | Level *              |
| [________________]     |           | [________________]| [A1 ▼]               |
|                        |           +------------------------------------------+
| Level *                |           | [Save] [Cancel]  [Delete]               |
| [A1             ▼]     |           +------------------------------------------+
|                        |
| [Save] [Cancel]        |
| [Delete]               |
+------------------------+
```

### CEFR Level Dropdown Options

```
+------------------+
| A1 (Beginner)    |  <-- Description shown in dropdown for user guidance
| A2 (Elementary)  |
| B1 (Intermediate)|
| B2 (Upper-Inter) |
| C1 (Advanced)    |
| C2 (Proficient)  |
+------------------+
```
Note: Descriptions shown in dropdown options for selection guidance, but only codes (A1, B2, etc.) display in saved items and resume output.

### Resume Preview - Languages Section

```
+------------------------------------------+
|  Languages                      [ON/OFF] |
+------------------------------------------+
|  English - C2                            |
|  French - B2                             |
|  Spanish - A2                            |
+------------------------------------------+
```

### Drag-and-Drop Interaction

```
Before drag:              During drag:           After drop:
⋮⋮ English - C2          ⋮⋮ English - C2        ⋮⋮ French - B2
⋮⋮ French - B2           ╔═══════════════╗      ⋮⋮ English - C2
⋮⋮ Spanish - A2          ║ French - B2   ║      ⋮⋮ Spanish - A2
                         ╚═══════════════╝
                         ⋮⋮ Spanish - A2
```

## Accessibility Checklist

- [x] All interactive elements keyboard accessible (Tab through items, Enter to select)
- [x] Focus states visible (follows existing app styles)
- [x] Form fields have labels (not just placeholders)
- [x] Select element for CEFR level (native, accessible)
- [x] Color contrast meets WCAG 2.1 AA (inherits from app theme)
- [x] Error states announced to screen readers (aria-invalid, role="alert")
- [x] Delete confirmation is a dialog with focus trap
- [x] Drag handles have aria-label for screen readers
- [x] Reorder announces position changes (aria-live region)

## Implementation Notes

1. **Follow Education.svelte pattern** - Most similar existing component (list with edit form)
2. **Drag-and-drop** - Use native HTML5 drag-and-drop or a library like `@dnd-kit` if already in use
3. **CEFR dropdown** - Show descriptions in options for guidance, store/display only code
4. **Order persistence** - Add `display_order` field, update via API on drag-drop
5. **Resume toggle** - Same pattern as Skills/Education sections

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Current state | C - Check codebase | Studied Skills.svelte, Education.svelte, ProfileEditor.svelte patterns |
| Preserve/rethink | A - Preserve existing patterns | Languages follows Education component structure |
| State review | A - Looks complete | 8 states confirmed (Empty, Loading, Loaded, Form, Saving, Success, Error, Delete Confirm) |
