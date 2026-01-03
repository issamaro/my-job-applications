# UX Design: Job-Tailored Resume Generation

**Date:** 2026-01-02
**Status:** Draft
**Design Philosophy:** Minimal. Focused. One task at a time. Follows Feature 1 patterns.

---

## 1. Navigation Model

Two views, tab-based navigation at top:

```
┌─────────────────────────────────────────────────────────────┐
│  MyCV     [Profile]  [Resume Generator]              [status]│
└─────────────────────────────────────────────────────────────┘
```

- **Profile** = Existing Feature 1 (profile editor)
- **Resume Generator** = New Feature 3 (this feature)
- Tab navigation, not routing (single page app continues)
- Active tab underlined

---

## 2. Layout: Resume Generator View

### 2.1 Input State (No Resume Generated Yet)

```
┌─────────────────────────────────────────────────────────────┐
│  MyCV     [Profile]  [Resume Generator]                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Generate Tailored Resume                                   │
│                                                             │
│  Paste a job description below. We'll analyze it and        │
│  create a resume highlighting your most relevant            │
│  experience.                                                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Paste job description here...                      │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Generate Resume]                                          │
│                                                             │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  History                                               [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ No resumes generated yet.                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Loading State (Generating)

```
┌─────────────────────────────────────────────────────────────┐
│  MyCV     [Profile]  [Resume Generator]                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Generate Tailored Resume                                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Senior Software Engineer - TechCorp                 │   │
│  │ We're looking for an experienced engineer...        │   │
│  │ (job description text, dimmed)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Analyzing job description...                               │
│  ████████████░░░░░░░░░░░░░░░░░░░░░                         │
│                                                             │
│  [Cancel]                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

- Progress bar (indeterminate or estimated)
- Job description locked (read-only, dimmed)
- Cancel option available

### 2.3 Result State (Resume Generated)

```
┌─────────────────────────────────────────────────────────────┐
│  MyCV     [Profile]  [Resume Generator]                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ← Back to Input                        Match Score: 78%    │
│                                                             │
│  Senior Software Engineer · TechCorp                        │
│  Generated Jan 2, 2026                                      │
│                                                             │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  Job Requirements                                      [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Required Skills                                     │   │
│  │   Python ✓   AWS ✓   SQL ✓   Docker ✓              │   │
│  │                                                     │   │
│  │ Preferred Skills                                    │   │
│  │   Kubernetes ✗   Terraform ✗   Go ✗                │   │
│  │                                                     │   │
│  │ Experience: 5+ years ✓                              │   │
│  │ Education: Bachelor's in CS ✓                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  Resume Preview                                             │
│                                                             │
│  Personal Info                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ John Smith                                          │   │
│  │ john@example.com · +1 555 123 4567                  │   │
│  │ San Francisco, CA · linkedin.com/in/johnsmith       │   │
│  │                                                     │   │
│  │ Experienced software engineer with 10+ years        │   │
│  │ building scalable web applications and APIs.        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Work Experience                            [ON]       [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. Senior Developer · Acme Corp                     │   │
│  │    Jan 2020 – Present                               │   │
│  │    ┌───────────────────────────────────────────┐   │   │
│  │    │ Led team of 5 engineers to build          │   │   │
│  │    │ customer-facing Python API using AWS...    │   │   │
│  │    └───────────────────────────────────────────┘   │   │
│  │    Match: Python, AWS, Team Leadership         [Edit]│  │
│  │                                                     │   │
│  │ 2. Developer · StartupCo                            │   │
│  │    Mar 2017 – Dec 2019                              │   │
│  │    Built REST APIs and microservices...             │   │
│  │    Match: SQL, Docker                          [Edit]│  │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Skills                                     [ON]       [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Python ✓] [AWS ✓] [SQL ✓] [Docker ✓] [React]      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Education                                  [ON]       [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BS Computer Science · State University · 2017       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Projects                                   [OFF]      [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ (Section hidden from resume)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ───────────────────────────────────────────────────────── │
│                                                             │
│  [Regenerate]                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. User Journeys

### Journey A: First-time resume generation

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Profile tab | Completed profile | Clicks "Resume Generator" tab | View switches |
| 2 | Generator tab | Empty textarea, instructions | Pastes job description | Text appears |
| 3 | Generator tab | Filled textarea | Clicks "Generate Resume" | Loading state |
| 4 | Loading | Progress bar, "Analyzing..." | Waits (10-30 sec) | Progress updates |
| 5 | Result | Match score, requirements, preview | Reviews resume | — |
| 6 | Result | Toggle switches, edit buttons | Optionally customizes | Changes apply |

### Journey B: Edit generated content

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Result | Work experience entry | Clicks "Edit" | Textarea expands inline |
| 2 | Editing | Editable description | Modifies text | — |
| 3 | Editing | Modified text | Clicks "Save" | "Saved" indicator, form collapses |

### Journey C: Toggle section visibility

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Result | Projects [OFF] toggle | Clicks toggle | Section shows as included |
| 2 | Result | Projects [ON] | Sees project content | Content visible |

### Journey D: View history and reload

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Input | History section | Clicks history item | Resume loads |
| 2 | Result | Previous resume | Reviews/edits | — |

### Journey E: Generate new resume (from result)

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Result | "Back to Input" link | Clicks link | Returns to input view |
| 2 | Input | Empty textarea | Pastes new JD | Ready to generate |

---

## 4. UI States

### Empty State (History)

```
┌─────────────────────────────────────────────────────────────┐
│  History                                               [▼]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ No resumes generated yet.                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Empty State (Profile incomplete)

When user has no work experience:

```
┌─────────────────────────────────────────────────────────────┐
│  Generate Tailored Resume                                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Your profile needs work experience before          │   │
│  │  you can generate a tailored resume.                │   │
│  │                                                     │   │
│  │  [Go to Profile]                                    │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Loading State

- **Trigger:** User clicks "Generate Resume"
- **Duration:** 10-30 seconds typical, up to 60 seconds timeout
- **Indicator:** Progress bar + status text
- **User can:** Cancel

```
Analyzing job description...
████████████░░░░░░░░░░░░░░░░░░░░░

[Cancel]
```

Status text progression:
1. "Analyzing job description..."
2. "Matching your experience..."
3. "Composing tailored resume..."

### Success State

- Match score prominently displayed
- Resume preview immediately visible
- No toast or modal — result is the feedback

### Error States

**Validation error (empty JD):**
```
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Paste job description here...                      │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  Please paste a job description (at least 100 characters)  │
│                                                             │
│  [Generate Resume]                                          │
└─────────────────────────────────────────────────────────────┘
```

**API error:**
```
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────┐   │
│  │ (job description text preserved)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Could not generate resume. Please try again.              │
│                                                             │
│  [Try Again]                                                │
└─────────────────────────────────────────────────────────────┘
```

**Timeout:**
```
┌─────────────────────────────────────────────────────────────┐
│  This is taking longer than expected...                     │
│                                                             │
│  [Keep Waiting]  [Cancel]                                   │
└─────────────────────────────────────────────────────────────┘
```

**Invalid job description:**
```
┌─────────────────────────────────────────────────────────────┐
│  This doesn't appear to be a job description.               │
│  Please paste a complete job posting.                       │
│                                                             │
│  [Try Again]                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Error Messages

| Error Type | Message | Recovery |
|------------|---------|----------|
| Empty input | "Please paste a job description (at least 100 characters)" | Type/paste content |
| Profile incomplete | "Your profile needs work experience before you can generate a tailored resume." | Link to Profile tab |
| API error | "Could not generate resume. Please try again." | Retry button |
| Timeout | "This is taking longer than expected..." | Keep waiting or Cancel |
| Invalid JD | "This doesn't appear to be a job description. Please paste a complete job posting." | Edit and retry |
| Save failed | "Could not save changes. Please try again." | Retry |

---

## 6. Component Specifications

### 6.1 Job Description Input

```
┌─────────────────────────────────────────────────────────────┐
│  Job Description *                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Paste job description here...                      │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  0 / 100 minimum characters                                 │
└─────────────────────────────────────────────────────────────┘
```

- Textarea: min-height 200px, resizable vertically
- Character counter updates as user types
- Placeholder: "Paste job description here..."
- Label above (not placeholder-as-label)

### 6.2 Match Score Badge

```
Match Score: 78%
```

- Positioned top-right of result view
- Color coding:
  - 80-100%: Green (#008800)
  - 60-79%: Default text color
  - 0-59%: Orange (#cc6600)
- No background, just text

### 6.3 Requirements Analysis Card

```
┌─────────────────────────────────────────────────────────────┐
│ Job Requirements                                       [▼]  │
├─────────────────────────────────────────────────────────────┤
│ Required Skills                                             │
│   Python ✓   AWS ✓   SQL ✓   Docker ✓                      │
│                                                             │
│ Preferred Skills                                            │
│   Kubernetes ✗   Terraform ✗   Go ✗                        │
│                                                             │
│ Experience: 5+ years ✓                                      │
│ Education: Bachelor's in CS ✓                               │
└─────────────────────────────────────────────────────────────┘
```

- Collapsible (default expanded)
- ✓ = matched (green #008800)
- ✗ = not matched (red #cc0000)
- Skills displayed inline as tags

### 6.4 Section Toggle

```
Work Experience                            [ON]       [▼]
```

- [ON] / [OFF] toggle button
- Appears after section title
- When OFF: section content shows "(Section hidden from resume)"
- Toggle is separate from collapse/expand

### 6.5 Inline Edit for Work Experience

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Senior Developer · Acme Corp                             │
│    Jan 2020 – Present                                       │
│    ┌───────────────────────────────────────────────────┐   │
│    │ Led team of 5 engineers to build customer-facing  │   │
│    │ Python API using AWS Lambda and DynamoDB...       │   │
│    │                                                   │   │
│    └───────────────────────────────────────────────────┘   │
│    [Save] [Cancel]                                          │
│    Match: Python, AWS, Team Leadership                      │
└─────────────────────────────────────────────────────────────┘
```

- Only description is editable (not title, dates, company)
- Textarea replaces static text when editing
- Save/Cancel buttons appear
- Original profile data NOT modified

### 6.6 History List

```
┌─────────────────────────────────────────────────────────────┐
│ History                                                [▼]  │
├─────────────────────────────────────────────────────────────┤
│ Senior Software Engineer · TechCorp         Jan 2, 2026    │
│ Match: 78%                                         [Delete] │
├─────────────────────────────────────────────────────────────┤
│ Backend Developer · StartupCo               Dec 28, 2025   │
│ Match: 65%                                         [Delete] │
└─────────────────────────────────────────────────────────────┘
```

- Click row to load resume
- Delete button at right (shows confirm dialog)
- Sorted by date descending (newest first)

---

## 7. Visual Design Notes

Following Feature 1 design system:

### Typography
- System font stack (same as Feature 1)
- Body: 16px
- Section headers: 20px
- Match score: 20px, bold

### Colors (extending Feature 1)
- Text: `#1a1a1a`
- Background: `#ffffff`
- Borders: `#e0e0e0`
- Primary action: `#0066cc`
- Error: `#cc0000`
- Success/Match: `#008800`
- Warning/Low match: `#cc6600`
- Progress bar: `#0066cc`

### Spacing
- 16px grid (same as Feature 1)
- 24px between major sections
- 12px between form fields

### New Elements
- Progress bar: 4px height, full width, `#0066cc` fill
- Toggle button: Text-based [ON]/[OFF], not switch
- Tab navigation: Underline for active, no background

---

## 8. Accessibility

- [x] All form fields have visible labels
- [x] Character counter announced to screen readers
- [x] Progress status announced via aria-live
- [x] Toggle buttons have aria-pressed state
- [x] Error messages linked with aria-describedby
- [x] Focus visible on all interactive elements
- [x] Tab navigation keyboard accessible
- [x] Match indicators have text (not color only): ✓/✗
- [x] History items keyboard navigable
- [x] Cancel/retry buttons keyboard accessible during loading

### Keyboard Shortcuts
- Tab: Navigate between elements
- Enter: Submit form / activate button
- Escape: Cancel editing / close expanded sections

---

## 9. Responsive Notes

Desktop-first (same as Feature 1). On narrow screens (< 600px):
- Full-width textarea
- Stack match score below title
- Requirement tags wrap
- Same functionality

Not a priority for MVP.

---

## 10. Interaction Timing

| Action | Feedback | Duration |
|--------|----------|----------|
| Click Generate | Loading state | Immediate |
| Generation complete | Result view | 10-30 sec typical |
| Save edit | "Saved" indicator | Immediate, fades after 2 sec |
| Toggle section | Visual update | Immediate |
| Delete history | Confirm dialog | User-controlled |

---

*Next: /v3-verify-analysis*
