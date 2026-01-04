# UX Design: Photo Management System

**Date:** 2026-01-04
**Status:** Draft

---

## 1. User Journeys

### Journey A: First-Time Photo Upload

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | PersonalInfo section | Upload zone with icon + "Add photo" text | Drags image or clicks zone | Zone highlights on dragover |
| 2 | Upload zone | File dialog opens | Selects image file | - |
| 3 | Upload zone | Brief validation | Waits | Spinner if validating |
| 4 | Photo Editor Modal | Cropper with image, toolbar, preview | Adjusts crop/rotate/zoom | Real-time preview updates |
| 5 | Photo Editor Modal | "Apply" and "Cancel" buttons | Clicks "Apply" | Modal shows saving spinner |
| 6 | PersonalInfo section | Photo displayed with edit/delete options | Continues with profile | "Saved" indicator appears |

### Journey B: Edit Existing Photo

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | PersonalInfo section | Photo with overlay "Change" + "Delete" | Clicks "Change" | - |
| 2 | File dialog | System file picker | Selects new image | - |
| 3 | Photo Editor Modal | Cropper with new image | Edits as desired | Preview updates |
| 4 | Photo Editor Modal | Apply/Cancel | Clicks "Apply" | Saving spinner |
| 5 | PersonalInfo section | New photo displayed | Continues | "Saved" indicator |

### Journey C: Delete Photo

| Step | Location | User Sees | User Does | Feedback |
|------|----------|-----------|-----------|----------|
| 1 | PersonalInfo section | Photo with "Delete" button | Clicks "Delete" | - |
| 2 | Confirm Dialog | "Delete your profile photo?" | Clicks "Delete" or "Cancel" | - |
| 3 | PersonalInfo section | Upload zone returns | Continues | "Photo deleted" toast |

---

## 2. UI States

### Upload Zone States

#### Empty State (No Photo)
- **Condition:** `photo === null`
- **Visual:** Circular dashed border, camera icon, "Add photo" text
- **Interaction:** Entire zone is clickable, supports drag-and-drop

```
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│                         │
│      📷 (icon)          │
│                         │
│   Add profile photo     │
│   Drag or click         │
│                         │
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

#### Drag-Over State
- **Condition:** File being dragged over zone
- **Visual:** Border becomes solid, background highlight
- **Message:** "Drop to upload"

#### Has Photo State
- **Condition:** `photo !== null`
- **Visual:** Photo thumbnail with hover overlay
- **Overlay:** "Change" and "Delete" buttons appear on hover

```
┌─────────────────────────┐
│                         │
│      [Photo]            │
│                         │
│   ┌────────┬────────┐   │ <- hover overlay
│   │ Change │ Delete │   │
│   └────────┴────────┘   │
└─────────────────────────┘
```

### Photo Editor Modal States

#### Loading State
- **Condition:** Image being processed
- **Visual:** Spinner in center of modal
- **Duration:** Brief, only for large images

#### Ready State
- **Condition:** Image loaded in cropper
- **Visual:** Full editor interface (see wireframe)

#### Saving State
- **Condition:** User clicked "Apply"
- **Visual:** "Apply" button shows spinner, all controls disabled
- **Message:** Button text: "Saving..."

### Validation Error States

| Error | Trigger | Message | Location |
|-------|---------|---------|----------|
| Invalid type | Non-image file selected | "Please upload an image (JPEG, PNG, or WebP)" | Toast notification |
| File too large | File > 10MB | "Image must be under 10MB" | Toast notification |
| Upload failed | Server error | "Could not upload photo. Please try again." | Toast notification |
| Save failed | Server error during save | "Could not save photo. Please try again." | Toast notification |

---

## 3. Error Messages

| Error | Message | Recovery |
|-------|---------|----------|
| Invalid file type | "Please upload an image (JPEG, PNG, or WebP)" | Select different file |
| File too large | "Image must be under 10MB" | Use smaller/compressed image |
| Upload failed | "Could not upload photo. Please try again." | Retry upload |
| Save failed | "Could not save photo. Please try again." | Retry save or cancel |
| Delete failed | "Could not delete photo. Please try again." | Retry delete |

---

## 4. Wireframes

### Upload Zone (Empty) - Integrated in PersonalInfo

```
┌─────────────────────────────────────────────────────────────────┐
│  Personal Information                                    Saved  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│       ╭───────────╮                                             │
│       │           │                                             │
│       │  📷       │         Name *         [John Doe        ]   │
│       │           │                                             │
│       │ Add photo │         Email *        [john@example.com]   │
│       │           │                                             │
│       ╰───────────╯         Phone          [+1 555-123-4567 ]   │
│       (drag/click)                                              │
│                             Location       [San Francisco, CA]  │
│                                                                 │
│                             LinkedIn       [linkedin.com/in/j]  │
│                                                                 │
│                             Summary                             │
│                             [                                ]  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Photo Display (Has Photo)

```
     ╭───────────╮
     │           │
     │   PHOTO   │
     │  (circle) │
     │           │
     ╰───────────╯
    ┌──────┬──────┐   <- visible on hover
    │Change│Delete│
    └──────┴──────┘
```

### Photo Editor Modal

```
┌─────────────────────────────────────────────────────────────────┐
│                                                             ✕   │
│  Edit Profile Photo                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────┐      ╭─────────╮      │
│  │  ┊        ┊        ┊                │      │         │      │
│  │──┼────────┼────────┼──              │      │ PREVIEW │      │
│  │  ┊  CROP  ┊  AREA  ┊   (3x3 grid)   │      │ (circle)│      │
│  │──┼────────┼────────┼──              │      │         │      │
│  │  ┊        ┊        ┊                │      ╰─────────╯      │
│  └─────────────────────────────────────┘                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ↻ Rotate                                     Reset     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Zoom: ──────●──────────────────────────────────────    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                      [ Cancel ]  [ Apply ]      │
└─────────────────────────────────────────────────────────────────┘
```

### Delete Confirmation Dialog

```
┌─────────────────────────────────────┐
│                                     │
│  Delete your profile photo?         │
│                                     │
│  This cannot be undone.             │
│                                     │
│          [ Cancel ]  [ Delete ]     │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Interaction Details

### Drag and Drop
- **Dragenter:** Zone border becomes solid, background lightens
- **Dragleave:** Returns to dashed border
- **Drop:** Validates file, opens editor if valid, shows error if invalid

### Cropper Controls
- **Crop area:** Fixed 1:1 square with 3x3 grid overlay for composition
- **Crop handles:** 8-point resize (corners + edges), maintains square ratio
- **Drag:** Move image within crop area
- **Rotate button:** Rotates 90° clockwise per click
- **Zoom slider:** Range 1x to 3x, affects image scale in crop area
- **Reset button:** Returns to initial crop/rotation/zoom state
- **Preview:** Circular preview showing final result

### Modal Behavior
- **Open:** Focus trapped in modal
- **Close:** Escape key or Cancel button
- **Backdrop click:** Closes modal (Cancel behavior)
- **Apply:** Saves and closes

---

## 6. Accessibility

- [x] Upload zone: `role="button"`, `aria-label="Upload profile photo"`
- [x] Drag-drop: Visual + aria-live announcement "File ready to drop"
- [x] Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- [x] Modal: Focus trapped, returns to trigger on close
- [x] Cropper: Keyboard controls for crop area adjustment
- [x] Zoom slider: `aria-valuemin`, `aria-valuemax`, `aria-valuenow`
- [x] Rotate: `aria-label="Rotate 90 degrees clockwise"`
- [x] All buttons: Visible focus rings
- [x] Errors: Announced via `aria-live="polite"` region
- [x] Color contrast: All text meets WCAG 2.1 AA (4.5:1)

### Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move between controls |
| Enter/Space | Activate button, open file picker |
| Escape | Close modal (Cancel) |
| Arrow keys | Adjust crop position (when cropper focused) |

---

## 7. Component Hierarchy

```
PersonalInfo.svelte
├── PhotoUpload.svelte (upload zone + photo display)
│   ├── Handles drag-and-drop
│   ├── Shows empty state or photo
│   ├── Edit/Delete buttons (when photo exists)
│   └── Opens PhotoEditor on upload/edit
│
└── PhotoEditor.svelte (modal)
    ├── Cropper.js integration
    ├── Toolbar (rotate, zoom, reset)
    ├── Preview panel
    └── Apply/Cancel actions
```

---

## 8. Visual Design Notes

### Colors (follow existing theme)
- Upload zone border: `var(--border-color)` dashed
- Drag-over highlight: `var(--primary-light)` or subtle blue
- Error messages: `var(--error-color)` (red)
- Success: `var(--success-color)` (green)

### Sizing
- Upload zone: 120px diameter circle
- Photo display: 120px diameter circle with `border-radius: 50%`
- Modal: Max 90vw × 90vh, centered
- Cropper area: Square with 3x3 grid, min 300px
- Preview: 120px diameter circle
- Output: 400x400px square (displayed as circle via CSS)

### Animation
- Modal: Fade in (200ms ease-out)
- Saved indicator: Fade out after 2s (match existing)
- Drag-over: Border transition (150ms)

---

*Next: /v4-verify-analysis*
