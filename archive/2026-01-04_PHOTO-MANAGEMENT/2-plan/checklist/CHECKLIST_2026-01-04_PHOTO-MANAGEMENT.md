# Checklist: Photo Management System

**Date:** 2026-01-04
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

| Requirement | Version | Verify | Status |
|-------------|---------|--------|--------|
| Python | 3.13 | `python --version` | [ ] |
| Node.js | 20.x | `node --version` | [ ] |
| uv | any | `uv --version` | [ ] |
| npm | any | `npm --version` | [ ] |

- [ ] Python virtual environment created (`.venv/`)
- [ ] Python virtual environment activated
- [ ] Node dependencies installed (`node_modules/`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

| Library | Constraint | Manifest | Status |
|---------|-----------|----------|--------|
| cropperjs | `^2.0.0` | package.json | [ ] |
| fastapi | `>=0.100.0` | requirements.txt | [ ] (existing) |
| pydantic | `>=2.0` | requirements.txt | [ ] (existing) |
| svelte | `^5.0.0` | package.json | [ ] (existing) |

- [ ] `npm install` completed after adding cropperjs
- [ ] Cropper.js CSS imported: `cropperjs/dist/cropper.css`

**STOP if any dependency is missing.**

---

## 2. Syntax

### Cropper.js v2 (Web Components)
- [ ] Import pattern: `import 'cropperjs'` (auto-registers custom elements)
- [ ] HTML uses web components: `<cropper-canvas>`, `<cropper-image>`, `<cropper-selection>`
- [ ] Fixed aspect ratio: `<cropper-selection aspectRatio="1">`
- [ ] Rotate method: `cropperImage.$rotate('90deg')`
- [ ] Export canvas: `await cropperSelection.$toCanvas({ width: 400, height: 400 })`
- [ ] To data URL: `canvas.toDataURL('image/jpeg', 0.85)`

### Svelte 5
- [ ] Use `onMount` for browser-only Cropper.js initialization
- [ ] Use `$state()` for reactive state (not `let`)
- [ ] Use `$effect()` for side effects (not `$:`)
- [ ] Dynamic import pattern for CSS: `await import('cropperjs/dist/cropper.css')`

### Pydantic v2
- [ ] Use `model_config = {"from_attributes": True}` (not `class Config`)
- [ ] Use `Field(...)` for field constraints
- [ ] Use `field_validator` decorator for custom validation

### FastAPI
- [ ] Router prefix: `/api/photos`
- [ ] Use Pydantic models for request/response
- [ ] Return 400 for validation errors, 404 for not found

---

## 3. UX

### Upload Zone States
- [ ] Empty state: Circular dashed border, camera icon, "Add profile photo", "Drag or click"
- [ ] Drag-over state: Solid border, background highlight, "Drop to upload"
- [ ] Has photo state: Circular photo, hover shows "Change" and "Delete" buttons

### Photo Editor Modal
- [ ] Modal title: "Edit Profile Photo"
- [ ] Cropper area with 3x3 grid overlay
- [ ] Circular preview (120px diameter)
- [ ] Rotate button with icon
- [ ] Zoom slider control
- [ ] Reset button
- [ ] Footer: "Cancel" and "Apply" buttons
- [ ] Saving state: "Apply" button shows spinner, text "Saving..."

### Error Messages (Toast Notifications)
- [ ] Invalid file type: "Please upload an image (JPEG, PNG, or WebP)"
- [ ] File too large: "Image must be under 10MB"
- [ ] Upload failed: "Could not upload photo. Please try again."
- [ ] Save failed: "Could not save photo. Please try again."
- [ ] Delete failed: "Could not delete photo. Please try again."

### Delete Flow
- [ ] Delete confirmation dialog: "Delete your profile photo?"
- [ ] Subtext: "This cannot be undone."
- [ ] Buttons: "Cancel" and "Delete"
- [ ] Success toast: "Photo deleted"

### Feedback
- [ ] "Saved" indicator appears after successful save (matches existing pattern)
- [ ] Loading spinner during upload/save operations

---

## 4. Tests

### API Tests (tests/test_photos.py)
- [ ] `test_get_photo_empty`: GET /api/photos returns null when no photo
- [ ] `test_upload_photo`: PUT /api/photos with valid data URL returns 200
- [ ] `test_get_photo_after_upload`: GET /api/photos returns uploaded photo
- [ ] `test_replace_photo`: PUT /api/photos replaces existing photo
- [ ] `test_delete_photo`: DELETE /api/photos removes photo
- [ ] `test_delete_photo_not_found`: DELETE /api/photos returns 404 when no photo
- [ ] `test_invalid_data_url_format`: PUT with invalid format returns 400
- [ ] `test_data_url_too_large`: PUT with oversized data returns 400

### Validation Tests
- [ ] Client-side: File type validation (JPEG, PNG, WebP only)
- [ ] Client-side: File size validation (max 10MB)
- [ ] Server-side: Data URL format regex validation
- [ ] Server-side: Data URL length validation (max 500,000 chars)

---

## 5. Accessibility

### Upload Zone
- [ ] `role="button"` on clickable upload zone
- [ ] `aria-label="Upload profile photo"` on upload zone
- [ ] `tabindex="0"` for keyboard focus
- [ ] Enter/Space activates file picker

### Drag and Drop
- [ ] `aria-live="polite"` region for drag state announcements
- [ ] Visual feedback for drag-over state

### Photo Editor Modal
- [ ] `role="dialog"` on modal
- [ ] `aria-modal="true"` on modal
- [ ] `aria-labelledby` pointing to modal title
- [ ] Focus trapped within modal
- [ ] Escape key closes modal
- [ ] Focus returns to trigger element on close

### Controls
- [ ] Zoom slider: `aria-label`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`
- [ ] Rotate button: `aria-label="Rotate 90 degrees clockwise"`
- [ ] All buttons have visible focus rings
- [ ] All interactive elements keyboard accessible

### Errors
- [ ] Error messages announced via `aria-live="polite"`

---

## 6. Project-Specific

None - no project-checks.md found.

---

## 7. Integration Points

### PersonalInfo.svelte Integration
- [ ] PhotoUpload component positioned left of form fields (per wireframe)
- [ ] Photo data flows to/from parent component
- [ ] Loading state coordinated with form loading state
- [ ] "Saved" indicator shared with existing save feedback

### API Integration
- [ ] `getPhoto()` called on component mount
- [ ] `uploadPhoto(dataUrl)` called on Apply
- [ ] `deletePhoto()` called on confirmed delete
- [ ] Error handling shows toast notifications

### Database Integration
- [ ] Migration adds `photo TEXT` column to `personal_info` table
- [ ] Migration is idempotent (try/except pattern)
- [ ] Photo data persists across app restarts

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v4-close`.

---

*Contract for /v4-implement*
