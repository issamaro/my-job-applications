# UX Design: Saved Job Descriptions

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Design System Reference

| Token | Value | Usage |
|-------|-------|-------|
| `$color-primary` | #0066cc | Links, focus states, primary actions |
| `$color-text` | #1a1a1a | Primary text |
| `$color-border` | #e0e0e0 | Borders, dividers |
| `$color-success` | #008800 | Success messages |
| `$color-error` | #cc0000 | Error messages, delete actions |
| `$spacing-grid` | 16px | Grid spacing |
| `$spacing-section` | 24px | Section margins |

---

## 2. User Journeys

### Journey A: Save a New Job Description

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Resume Generator tab | Empty JD input area | Pastes job description text | Character counter updates |
| 2 | JD Input area | "125 / 100 minimum characters" (green) | Clicks "Save" button | Button shows "Saving..." |
| 3 | JD Input area | Toast appears | Waits | "Job description saved" (3s) |
| 4 | Saved JDs panel | New item appears at top of list | Can continue to generate or save another | Item shows "Untitled Job" |

### Journey B: Load and Generate from Saved JD

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Saved JDs panel | List of saved JDs | Clicks on a JD item | JD loads into input area |
| 2 | JD Input area | JD text populated, "Generate" active | Clicks "Generate Resume" | Progress bar appears |
| 3 | Loading state | Status messages cycle | Waits | "Analyzing...", "Matching...", "Composing..." |
| 4 | Preview | Generated resume displayed | Reviews resume | Match score, sections visible |
| 5 | Saved JDs panel | Resume count badge updates | - | "(2 resumes)" shown on JD item |

### Journey C: Edit Saved JD and Regenerate

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Saved JDs panel | Saved JD list | Clicks on a JD | JD loads into input |
| 2 | JD Input area | JD text populated | Edits text (adds details) | Character count updates |
| 3 | JD Input area | Modified text | Clicks "Generate Resume" | "Updating and generating..." |
| 4 | Preview | New resume with updated match | Reviews | JD saved with new version |

### Journey D: Rename a Saved JD

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Saved JDs panel | JD item with title | Clicks pencil icon next to title | Title becomes editable |
| 2 | JD item | Text input with current title | Types new title | Input border highlights |
| 3 | JD item | New title in input | Presses Enter or clicks away | Title saves, input becomes text |
| 4 | Saved JDs panel | Updated title displayed | Continues | No toast (inline feedback sufficient) |

### Journey E: Delete a Saved JD

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Saved JDs panel | JD item with delete link | Clicks "Delete" | Confirmation dialog opens |
| 2 | Dialog | "Delete this job description?" | Reads warning about resumes | Message shows resume count |
| 3 | Dialog | Delete/Cancel buttons | Clicks "Delete" | Dialog closes, item fades out |
| 4 | Saved JDs panel | Item removed from list | Continues | Toast: "Job description deleted" |

---

## 3. UI States

### 3.1 JD Input Area States

| State | Condition | Visual | Actions Available |
|-------|-----------|--------|-------------------|
| **Empty** | No text entered | Placeholder visible | None (buttons disabled) |
| **Partial** | < 100 chars | Counter red, "75 / 100" | None (buttons disabled) |
| **Valid** | >= 100 chars | Counter green | Save, Generate |
| **Loading (save)** | Saving in progress | Save button: "Saving..." | Cancel generation only |
| **Loading (generate)** | Generating | Textarea dimmed, progress bar | Cancel |
| **Loaded from saved** | JD loaded from panel | Blue indicator bar on left | Save, Generate, Clear |

### 3.2 Saved JDs Panel States

| State | Condition | User Sees | User Can Do |
|-------|-----------|-----------|-------------|
| **Empty** | No saved JDs | Empty message + hint | Paste and save a JD |
| **Loading** | Fetching list | Skeleton (3 items) | Wait |
| **Loaded** | JDs exist | List of JD items | Click, edit title, delete |
| **Item selected** | JD loaded in input | Highlighted item (blue left border) | See which JD is active |

### 3.3 Individual JD Item States

| State | Condition | Visual | Actions |
|-------|-----------|--------|---------|
| **Normal** | Default | Title, preview, meta | Click to load, edit title, delete |
| **Selected** | Loaded in input | Blue left border, subtle bg | Same |
| **Editing title** | Title clicked | Inline input field | Type, Enter to save, Esc to cancel |
| **Expanded** | Clicked expand | Shows linked resumes | Collapse, click resume |

---

## 4. Component Specifications

### 4.1 JobDescriptionInput (Modified)

```
┌─────────────────────────────────────────────────────────────┐
│ Generate Tailored Resume                                    │
│                                                             │
│ Paste a job description below. We'll analyze it and        │
│ create a resume highlighting your most relevant experience. │
├─────────────────────────────────────────────────────────────┤
│ Job Description *                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ We are looking for a Senior Software Engineer...       │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ 245 / 100 minimum characters                                │
│                                                             │
│ ┌─────────────┐  ┌──────────────────┐                       │
│ │    Save     │  │ Generate Resume  │                       │
│ └─────────────┘  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Button States:**
- **Save**: `btn` style, disabled if < 100 chars
- **Generate Resume**: `btn btn-primary` style, disabled if < 100 chars

**Loaded State Indicator:**
```
┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐
│ ┌────────────────────────────────────────────────┐ [Clear] │
│ │ (blue) Editing: Senior Engineer at TechCorp   │         │
│ └────────────────────────────────────────────────┘         │
└─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
```

### 4.2 SavedJobsList (New Component)

```
┌─────────────────────────────────────────────────────────────┐
│ ┌─ Saved Job Descriptions ─────────────────────────── [-] ─┐│
│ │                                                          ││
│ │ ┌────────────────────────────────────────────────────┐   ││
│ │ │ Senior Software Engineer at TechCorp         [✎]  │   ││
│ │ │ We are looking for a senior engineer to join...    │   ││
│ │ │ Jan 3, 2026 · 2 resumes                   [Delete] │   ││
│ │ └────────────────────────────────────────────────────┘   ││
│ │                                                          ││
│ │ ┌────────────────────────────────────────────────────┐   ││
│ │ │ Product Manager at StartupXYZ              [✎]    │   ││
│ │ │ Seeking a product manager to lead our mobile...    │   ││
│ │ │ Jan 2, 2026 · 1 resume                    [Delete] │   ││
│ │ └────────────────────────────────────────────────────┘   ││
│ │                                                          ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Empty State:**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌─ Saved Job Descriptions ─────────────────────────── [-] ─┐│
│ │                                                          ││
│ │    No saved job descriptions yet.                        ││
│ │                                                          ││
│ │    Paste a job description above and click               ││
│ │    "Save" to keep it for later.                          ││
│ │                                                          ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 4.3 SavedJobItem (New Component)

**Normal State:**
```
┌────────────────────────────────────────────────────────────┐
│ Senior Software Engineer at TechCorp                 [✎]   │
│ We are looking for a senior engineer to join our team...   │
│ Jan 3, 2026 · 2 resumes                            [Delete] │
└────────────────────────────────────────────────────────────┘
```

**Selected State (loaded in input):**
```
┌────────────────────────────────────────────────────────────┐
│▌Senior Software Engineer at TechCorp                [✎]   │
│▌We are looking for a senior engineer to join our team...  │
│▌Jan 3, 2026 · 2 resumes                           [Delete] │
└────────────────────────────────────────────────────────────┘
  ↑ Blue left border indicates selection
```

**Editing Title State:**
```
┌────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────┐ [✓]   │
│ │ Senior Software Engineer at TechCorp            │        │
│ └──────────────────────────────────────────────────┘        │
│ We are looking for a senior engineer to join our team...   │
│ Jan 3, 2026 · 2 resumes                            [Delete] │
└────────────────────────────────────────────────────────────┘
```

**Expanded State (showing linked resumes):**
```
┌────────────────────────────────────────────────────────────┐
│ Senior Software Engineer at TechCorp                 [✎]   │
│ We are looking for a senior engineer to join our team...   │
│ Jan 3, 2026 · 2 resumes                  [▼]       [Delete] │
├────────────────────────────────────────────────────────────┤
│   → Resume v2 · Jan 3, 2026 · Match: 87%                   │
│   → Resume v1 · Jan 3, 2026 · Match: 82%                   │
└────────────────────────────────────────────────────────────┘
```

### 4.4 Overall Layout

**Desktop (>= 768px):**
```
┌─────────────────────────────────────────────────────────────────────┐
│                        Resume Generator                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Job Description Input                      │    │
│  │                   (textarea + buttons)                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ═══════════════════════════════════════════════════════════════    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               Saved Job Descriptions                         │    │
│  │               (collapsible panel)                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Resume History                             │    │
│  │               (existing component)                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Mobile (< 768px):**
- Same layout, full width
- Touch targets minimum 44x44px
- Buttons stack vertically when needed

---

## 5. Error Messages

| Error | User Message | Recovery |
|-------|--------------|----------|
| Empty JD (save) | "Please enter a job description" | Focus textarea |
| Too short (save) | "Job description must be at least 100 characters" | Keep typing |
| Save failed | "Could not save. Please try again." | Retry button |
| Load failed | "Could not load job descriptions. Please refresh." | Refresh page |
| Delete failed | "Could not delete. Please try again." | Close dialog, retry |
| Title too long | "Title must be 100 characters or less" | Shorten title |

---

## 6. Toast Messages

| Action | Type | Message | Duration |
|--------|------|---------|----------|
| JD saved | success | "Job description saved" | 3s |
| JD updated | success | "Job description updated" | 3s |
| JD deleted | success | "Job description deleted" | 3s |
| Title updated | (none) | (inline feedback sufficient) | - |
| Save error | error | "Could not save. Please try again." | 3s |

---

## 7. Confirmation Dialogs

### Delete Job Description

```
┌──────────────────────────────────────────────┐
│                                              │
│   Delete Job Description?                    │
│                                              │
│   This will also delete 2 generated resumes  │
│   linked to this job description.            │
│                                              │
│   This action cannot be undone.              │
│                                              │
│           [Cancel]    [Delete]               │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 8. Keyboard Navigation

| Key | Context | Action |
|-----|---------|--------|
| Tab | Any | Move focus to next interactive element |
| Enter | On JD item | Load JD into input |
| Enter | Title editing | Save title |
| Escape | Title editing | Cancel editing, restore original |
| Escape | Confirm dialog | Close dialog (cancel) |
| Space | On expand button | Toggle expand/collapse |

---

## 9. Accessibility Requirements

- [x] All interactive elements keyboard accessible
- [x] Focus states visible (2px solid $color-primary)
- [x] Form fields have labels (not just placeholders)
- [x] Color contrast WCAG 2.1 AA (4.5:1 text, 3:1 UI)
- [x] Error states announced to screen readers (`role="alert"`)
- [x] Loading states communicated (`aria-busy="true"`)
- [x] Delete confirmation is modal (`role="dialog"`, `aria-modal="true"`)
- [x] Selected state communicated (`aria-current="true"`)

**ARIA Labels:**
- Save button: `aria-label="Save job description"`
- Edit title button: `aria-label="Edit job description title"`
- Delete button: `aria-label="Delete job description"`
- JD item: `aria-label="[Title], [date], [n] resumes. Click to load."`

---

## 10. Component Hierarchy

```
ResumeGenerator.svelte
├── JobDescriptionInput.svelte (modified)
│   ├── textarea
│   ├── character counter
│   ├── loaded-indicator (new)
│   └── button row (Save + Generate)
│
├── SavedJobsList.svelte (new)
│   ├── collapsible header
│   ├── empty state
│   └── SavedJobItem.svelte (new) × n
│       ├── title (editable)
│       ├── text preview
│       ├── meta (date, resume count)
│       ├── expand toggle (optional)
│       ├── linked resumes list (when expanded)
│       └── delete button
│
├── ProgressBar.svelte (existing)
├── ResumePreview.svelte (existing)
├── ResumeHistory.svelte (existing)
├── ConfirmDialog.svelte (reused)
└── Toast.svelte (reused)
```

---

## 11. SCSS Files Needed

| File | Purpose |
|------|---------|
| `views/_saved-jobs.scss` | SavedJobsList and SavedJobItem styles |
| `views/_resume-generator.scss` | Modifications for loaded indicator |

**Reuse existing patterns from:**
- `views/_history.scss` - collapsible panel, list items
- `components/_buttons.scss` - button styles
- `components/_forms.scss` - inline editing input

---

*Next: /v3-verify-analysis*
