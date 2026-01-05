# UX Design: Import JSON Profile

**Date:** 2026-01-04
**Status:** Draft
**Approach:** One button for the whole feature, rest is on the modal

---

## 1. User Journey

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | Profile Editor (top) | Single "Import JSON" button | Clicks button | Modal opens |
| 2 | Import Modal | Upload area + "Download Sample" link | Needs sample? Clicks download | JSON file downloads |
| 3 | Import Modal | Upload area (drag-drop or click) | Selects/drops JSON file | Validation starts |
| 4 | Import Modal | Spinner while validating | Waits briefly | Loading state |
| 5a | Import Modal | Preview summary + warning + "Import" button | Reviews counts, clicks "Import" | Import starts |
| 5b | Import Modal (error) | Error message with specific issue | Reads error, tries different file | Can retry |
| 6 | Import Modal | "Importing..." state | Waits | Spinner on Import button |
| 7 | Profile Editor | Modal closes, sections refresh | Sees updated profile | Success toast |

---

## 2. UI States

### Profile Editor - Idle
- **Condition:** No import in progress
- **UI:** Single "Import JSON" button in toolbar area
- **User can:** Click to open Import Modal

### Import Modal - Initial (No File)
- **Condition:** Modal just opened, no file selected
- **UI:**
  - Upload drop zone (drag-drop or click to browse)
  - "Download Sample JSON" link below the drop zone
  - "Cancel" button
- **User can:** Upload file, download sample, or cancel

### Import Modal - Validating
- **Condition:** File selected, parsing/validating
- **Indicator:** Spinner in upload zone, "Validating..." text
- **User can:** Wait

### Import Modal - Preview (Valid File)
- **Condition:** Valid JSON parsed and validated
- **UI:**
  - Preview summary (item counts per section)
  - Warning about data replacement
  - Photo preservation note
  - "Cancel" and "Import" buttons
- **User can:** Confirm import, cancel, or select different file

### Import Modal - Error
- **Condition:** Invalid JSON or validation failed
- **UI:**
  - Error message with specific issue(s)
  - Upload zone to try different file
  - "Download Sample JSON" link still visible
- **User can:** Try different file, download sample, or cancel

### Import Modal - Importing
- **Condition:** User confirmed, API call in progress
- **Indicator:** "Importing..." on button, spinner
- **User can:** Wait (buttons disabled)

### Success State
- **Action:** Modal closes automatically
- **Message:** "Profile imported successfully" (Toast)
- **Duration:** Auto-dismisses after 3 seconds
- **Next:** ProfileEditor refreshes with new data

---

## 3. Error Messages

| Error | Message | Recovery |
|-------|---------|----------|
| Invalid JSON syntax | "Invalid JSON: Unexpected token at position X" | Fix JSON syntax |
| Missing personal_info | "Missing required section: personal_info" | Add section to JSON |
| Missing full_name | "Missing required field: personal_info.full_name" | Add field to JSON |
| Missing email | "Missing required field: personal_info.email" | Add field to JSON |
| Invalid graduation_year | "Invalid type: education[0].graduation_year must be a number" | Fix data type |
| Wrong structure | "work_experiences must be an array" | Fix JSON structure |
| Server error | "Import failed. Please try again." | Retry |
| File read error | "Could not read file. Please try again." | Re-select file |

---

## 4. Wireframes

### Profile Editor - Single Button

```
┌─────────────────────────────────────────────────────────┐
│                                    ┌───────────────┐    │
│                                    │  Import JSON  │    │
│                                    └───────────────┘    │
│                                                         │
│  ▼ Personal Info                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [Photo]   Full Name: _______________           │   │
│  │            Email: _______________               │   │
│  │            ...                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ▼ Work Experience                        [+ Add]       │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

### Import Modal - Initial State (No File)

```
┌──────────────────────────────────────────────────────────┐
│  Import Profile                                      ✕   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │                                                    │ │
│  │           ┌───┐                                    │ │
│  │           │ ↑ │                                    │ │
│  │           └───┘                                    │ │
│  │                                                    │ │
│  │     Drag & drop your JSON file here               │ │
│  │              or click to browse                   │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Don't have a JSON file?                                │
│  Download Sample JSON to see the expected format.       │
│                                                          │
│  ┌──────────┐                                           │
│  │  Cancel  │                                           │
│  └──────────┘                                           │
└──────────────────────────────────────────────────────────┘
```

### Import Modal - Preview State (Valid File)

```
┌──────────────────────────────────────────────────────────┐
│  Import Profile                                      ✕   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Ready to import:                                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • Personal Info    will be updated                │ │
│  │  • Work Experience  3 items                        │ │
│  │  • Education        2 items                        │ │
│  │  • Skills           8 items                        │ │
│  │  • Projects         4 items                        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ⚠ This will replace all existing data.                 │
│    Your profile photo will be preserved.                │
│                                                          │
│  ┌──────────┐  ┌───────────────────┐                    │
│  │  Cancel  │  │      Import       │                    │
│  └──────────┘  └───────────────────┘                    │
│                                                          │
│  ── or select a different file ──                       │
└──────────────────────────────────────────────────────────┘
```

### Import Modal - Error State

```
┌──────────────────────────────────────────────────────────┐
│  Import Profile                                      ✕   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  ✗ Validation failed:                              │ │
│  │                                                    │ │
│  │  • Missing required field: personal_info.email    │ │
│  │  • work_experiences[0].start_date must be YYYY-MM │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │     Drag & drop a different file                   │ │
│  │           or click to browse                       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Need help? Download Sample JSON                        │
│                                                          │
│  ┌──────────┐                                           │
│  │  Cancel  │                                           │
│  └──────────┘                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 5. Accessibility

- [x] Keyboard navigation: Tab through all interactive elements in modal
- [x] Focus indicators: Standard button/link focus styles
- [x] Focus management:
  - Focus moves to modal when opened
  - Focus trapped inside modal while open
  - Focus returns to "Import JSON" button when modal closes
- [x] Form labels: N/A (file input is hidden, triggered by labeled drop zone)
- [x] Color contrast: Follow existing button styles
- [x] Screen reader support:
  - Modal: role="dialog", aria-modal="true", aria-labelledby="modal-title"
  - Drop zone: aria-label="Upload JSON file, drag and drop or click to browse"
  - Loading state: aria-busy="true", aria-live="polite" for status updates
  - Error messages: aria-live="assertive" for validation errors
  - Success: Toast with role="status", aria-live="polite"
- [x] Escape key closes modal
- [x] Drop zone accessible via Enter/Space

---

## 6. Component Breakdown

### New Components

| Component | Purpose |
|-----------|---------|
| `ImportModal.svelte` | Full-featured modal: file upload, validation, preview, sample download |

### Reused Components

| Component | Usage |
|-----------|-------|
| `Toast.svelte` | Success feedback after modal closes |

### Component Hierarchy

```
ProfileEditor.svelte
├── "Import JSON" button (triggers modal)
├── ImportModal.svelte (NEW) - conditionally rendered
│   ├── Modal backdrop + container
│   ├── Header with close button
│   ├── Drop zone (drag-drop + click to browse)
│   ├── Hidden file input
│   ├── "Download Sample JSON" link
│   ├── Preview summary (when valid file loaded)
│   ├── Error display (when validation fails)
│   └── Action buttons (Cancel / Import)
├── Toast (for success message after import)
├── Section (Personal Info)
│   └── PersonalInfo.svelte
├── Section (Work Experience)
│   └── WorkExperience.svelte
└── ...
```

---

## 7. Interaction Details

### Modal Open/Close
- "Import JSON" button in ProfileEditor opens modal
- Modal closes on: Cancel click, X button, Escape key, backdrop click, successful import
- Focus trapped inside modal while open

### File Selection (Inside Modal)
- Drop zone supports drag-drop and click-to-browse
- Hidden `<input type="file" accept=".json">`
- On file select: read file, parse JSON, validate schema
- Can select new file at any state (replaces current)

### Sample JSON Download
- "Download Sample JSON" link triggers browser download
- Static JSON file with example data
- Available in initial state and error state

### Validation Flow
1. Parse JSON (catch syntax errors)
2. Validate structure (required sections exist)
3. Validate required fields in each section
4. Collect all errors, show first 5 if many
5. If valid → show preview; if invalid → show errors

### Preview & Confirmation
- Shows item counts per section (not full data)
- Warning about data replacement
- Photo preservation note
- "Import" button to proceed, "Cancel" to close
- Option to select different file without closing

### Post-Import Refresh
- After successful import, modal closes automatically
- Toast shows "Profile imported successfully"
- Components need to reload data
- **Recommendation:** Use page reload for MVP, optimize later if needed

---

## 8. Sample JSON Download

A static JSON file with example data:

```json
{
  "personal_info": {
    "full_name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/janedoe",
    "summary": "Experienced software engineer..."
  },
  "work_experiences": [
    {
      "company": "Tech Corp",
      "title": "Senior Engineer",
      "location": "San Francisco, CA",
      "start_date": "2020-01",
      "end_date": null,
      "is_current": true,
      "description": "Lead development of..."
    }
  ],
  "education": [
    {
      "institution": "State University",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "graduation_year": 2018,
      "gpa": 3.8,
      "notes": ""
    }
  ],
  "skills": [
    { "name": "JavaScript" },
    { "name": "Python" },
    { "name": "React" }
  ],
  "projects": [
    {
      "name": "Open Source Tool",
      "description": "A CLI tool for...",
      "technologies": "Node.js, TypeScript",
      "url": "https://github.com/example/tool",
      "start_date": "2022-06",
      "end_date": "2022-12"
    }
  ]
}
```

---

*Next: /v4-verify-analysis*
