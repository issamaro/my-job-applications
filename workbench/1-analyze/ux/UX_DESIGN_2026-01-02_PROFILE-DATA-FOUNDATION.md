# UX Design: Profile Data Foundation

**Date:** 2026-01-02
**Status:** Draft
**Design Philosophy:** Minimal. No visual noise. Forms that get out of the way.

---

## 1. Layout

Single page. Vertical scroll. No sidebar. No tabs.

```
┌─────────────────────────────────────────────────────────────┐
│  MyCV                                              [status] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Personal Info                                        [▼]   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Name        [________________________]              │   │
│  │ Email       [________________________]              │   │
│  │ Phone       [________________________]              │   │
│  │ Location    [________________________]              │   │
│  │ LinkedIn    [________________________]              │   │
│  │ Summary     [________________________]              │   │
│  │             [________________________]              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Work Experience                              [+ Add]  [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Senior Developer · Acme Corp                        │   │
│  │ Jan 2020 – Present · San Francisco            [Edit]│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Developer · StartupCo                               │   │
│  │ Mar 2017 – Dec 2019 · Remote                  [Edit]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Education                                    [+ Add]  [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BS Computer Science · State University              │   │
│  │ 2017                                          [Edit]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Skills                                       [+ Add]  [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Python ×] [FastAPI ×] [Svelte ×] [SQL ×]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Projects                                     [+ Add]  [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Portfolio Site                                      │   │
│  │ Personal website built with Svelte            [Edit]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. User Journeys

### Journey A: First-time user fills profile

| Step | User Sees | User Does | Feedback |
|------|-----------|-----------|----------|
| 1 | Empty sections with placeholder text | Clicks into Name field | Field focuses |
| 2 | Personal Info form | Fills fields, tabs through | Auto-saves on blur |
| 3 | "Saved" indicator appears briefly | Continues to Work Experience | Indicator fades |
| 4 | Empty Work Experience section | Clicks "+ Add" | Inline form expands |
| 5 | Work Experience form | Fills company, title, dates, description | — |
| 6 | Filled form | Clicks "Save" | Entry appears in list, form collapses |
| 7 | Work entry in list | Repeats for Education, Skills, Projects | — |

### Journey B: Edit existing entry

| Step | User Sees | User Does | Feedback |
|------|-----------|-----------|----------|
| 1 | Work Experience list | Clicks "Edit" on entry | Form expands inline below entry |
| 2 | Filled form | Changes title | — |
| 3 | Edited form | Clicks "Save" | Entry updates, form collapses |

### Journey C: Delete entry

| Step | User Sees | User Does | Feedback |
|------|-----------|-----------|----------|
| 1 | Edit form open | Clicks "Delete" (text link, not button) | Confirm dialog appears |
| 2 | "Delete this entry?" | Clicks "Delete" | Entry removed, form collapses |

---

## 3. UI States

### Empty State
Each section when no data exists:

```
┌─────────────────────────────────────────────────────────────┐
│  Work Experience                              [+ Add]  [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │           No work experience added yet.             │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

- No icons. No illustrations. Just text.
- "+ Add" button is already visible in header.

### Loading State
- On initial page load: skeleton lines where text will be
- On save: button shows "Saving..." then reverts
- No spinners. No progress bars.

### Success State
- Small "Saved" text appears next to section header
- Fades after 2 seconds
- No toast notifications. No modals.

### Error State
- Field-level: red border + message below field
- Form-level: message at top of form
- Never blocks the UI

---

## 4. Interaction Details

### Auto-save (Personal Info only)
- Personal Info saves on field blur (lose focus)
- Shows "Saved" indicator
- No explicit Save button for Personal Info

### Explicit Save (List items)
- Work, Education, Projects require clicking "Save"
- Forms have: [Save] [Cancel] ... [Delete]
- Delete is a text link, not a button (less prominent)

### Inline Editing
- No modals. Ever.
- Forms expand inline below the section header or below the item being edited
- Only one form open at a time per section

### Collapse/Expand
- Sections can collapse to hide content
- Click section header or [▼] to toggle
- All expanded by default
- State not persisted (always expanded on load)

### Skills Input
- Text input with comma parsing
- Type "Python, FastAPI, SQL" → creates 3 tags
- Click × on tag to remove
- No proficiency selector in MVP (simplify)

---

## 5. Forms

### Personal Info
```
┌─────────────────────────────────────────────────────────────┐
│  Name *        [John Smith_________________________]        │
│  Email *       [john@example.com___________________]        │
│  Phone         [+1 555 123 4567____________________]        │
│  Location      [San Francisco, CA__________________]        │
│  LinkedIn      [linkedin.com/in/johnsmith__________]        │
│  Summary       [Experienced software engineer with  ]       │
│                [10+ years building web applications.]       │
│                [________________________________________]   │
└─────────────────────────────────────────────────────────────┘
* Required fields
Auto-saves on blur
```

### Work Experience Form
```
┌─────────────────────────────────────────────────────────────┐
│  Company *     [Acme Corp__________________________]        │
│  Title *       [Senior Developer___________________]        │
│  Location      [San Francisco, CA__________________]        │
│  Start *       [2020-01] (month picker)                     │
│  End           [________] (month picker)  [ ] Current       │
│  Description   [Led team of 5 engineers to build    ]       │
│                [customer-facing API. Reduced latency ]      │
│                [by 40% through caching improvements. ]      │
│                                                             │
│  [Save]  [Cancel]                              Delete       │
└─────────────────────────────────────────────────────────────┘
```

### Education Form
```
┌─────────────────────────────────────────────────────────────┐
│  Institution * [State University___________________]        │
│  Degree *      [BS___] Field [Computer Science_____]        │
│  Year          [2017]                                       │
│  Notes         [Graduated magna cum laude__________]        │
│                                                             │
│  [Save]  [Cancel]                              Delete       │
└─────────────────────────────────────────────────────────────┘
```

### Project Form
```
┌─────────────────────────────────────────────────────────────┐
│  Name *        [Portfolio Website__________________]        │
│  URL           [https://johnsmith.dev______________]        │
│  Technologies  [Svelte, Sass, Python_______________]        │
│  Description   [Personal portfolio and blog built   ]       │
│                [from scratch. Features dark mode.   ]       │
│                                                             │
│  [Save]  [Cancel]                              Delete       │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Error Messages

| Context | Message | Display |
|---------|---------|---------|
| Required field empty | "Required" | Below field, red |
| Invalid email | "Invalid email address" | Below field, red |
| Invalid date | "Invalid date" | Below field, red |
| End date before start | "End date must be after start date" | Below End field, red |
| Save failed | "Could not save. Please try again." | Top of form, red |
| Load failed | "Could not load profile. Please refresh." | Center of page |

---

## 7. Visual Design Notes

### Typography
- System font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- One size for body (16px), one for headings (20px)
- No bold except section headers

### Colors
- Text: `#1a1a1a` (near black)
- Background: `#ffffff`
- Borders: `#e0e0e0`
- Primary action: `#0066cc` (blue)
- Error: `#cc0000` (red)
- Success: `#008800` (green, for "Saved" text only)

### Spacing
- Consistent 16px grid
- 24px between sections
- 12px between form fields

### No:
- Shadows
- Rounded corners (or minimal: 2px)
- Gradients
- Icons (except × for tag removal)
- Animations (except fade for "Saved" indicator)

---

## 8. Accessibility

- [x] All form fields have visible labels (not placeholders as labels)
- [x] Required fields marked with * and `aria-required`
- [x] Error messages linked with `aria-describedby`
- [x] Focus visible on all interactive elements (2px blue outline)
- [x] Delete confirmation is a dialog, not just a click
- [x] Color contrast: all text meets WCAG AA (4.5:1+)
- [x] Keyboard: Tab through fields, Enter to submit, Escape to cancel

---

## 9. Responsive Notes

Desktop-first. On narrow screens (< 600px):
- Full-width forms
- Stack label above input (not beside)
- Same functionality, just reflowed

Not a priority for MVP. Desktop works.

---

*Next: /v3-verify-analysis*
