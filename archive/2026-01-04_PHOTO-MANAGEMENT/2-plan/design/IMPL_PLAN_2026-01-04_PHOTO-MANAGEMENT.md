# Implementation Plan: Photo Management System

**Date:** 2026-01-04
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-04_PHOTO-MANAGEMENT.md

---

## 1. Affected Files

### Config/Dependencies
| File | Change | Description |
|------|--------|-------------|
| `package.json` | Modify | Add `cropperjs@^2.0.0` dependency |

### Backend
| File | Change | Description |
|------|--------|-------------|
| `database.py` | Modify | Add migration for `photo` column in `personal_info` table |
| `schemas.py` | Modify | Add `PhotoUpload`, `PhotoResponse` schemas; add `photo` field to `PersonalInfo` |
| `routes/photos.py` | Create | New router with GET/PUT/DELETE endpoints for photo CRUD |
| `routes/__init__.py` | Modify | Register photos router |
| `main.py` | Modify | Include photos router (if not auto-discovered) |

### Frontend
| File | Change | Description |
|------|--------|-------------|
| `src/components/PhotoUpload.svelte` | Create | Upload zone component (drag-drop, file picker, photo display) |
| `src/components/PhotoEditor.svelte` | Create | Modal with Cropper.js integration (crop, rotate, zoom, preview) |
| `src/components/PersonalInfo.svelte` | Modify | Integrate PhotoUpload component |
| `src/lib/api.js` | Modify | Add photo API functions (getPhoto, uploadPhoto, deletePhoto) |

### Tests
| File | Change | Description |
|------|--------|-------------|
| `tests/test_photos.py` | Create | API tests for photo endpoints |

---

## 2. Database Changes

```sql
-- Migration: Add photo column to personal_info
ALTER TABLE personal_info ADD COLUMN photo TEXT;
```

**Notes:**
- `photo` stores base64 data URL: `data:image/jpeg;base64,{encoded_data}`
- TEXT type sufficient for ~50-150KB base64 strings (400x400 JPEG at 85%)
- Migration pattern matches existing (try/except for idempotency)

---

## 3. Implementation Approach

### Architecture: Client-Side Processing

All image processing happens **client-side** via Cropper.js v2:
- User selects image → opens in PhotoEditor modal
- User crops (1:1 square), rotates (90°), zooms
- On "Apply": Cropper.js exports to 400x400 canvas → JPEG at 85% → base64 data URL
- Frontend sends data URL to backend
- Backend validates format/size and stores in database

**Why client-side:**
- No server-side image library needed (simpler backend)
- Faster uploads (smaller processed image sent)
- Less server CPU usage

### Service Pattern

Photo operations are simple CRUD on a single field. No separate service file needed - route handlers are sufficient (matches existing pattern for simple operations like skills).

### Validation

**Client-side (first line):**
- File type: JPEG, PNG, WebP only
- File size: max 10MB (before processing)
- Cropper.js handles aspect ratio enforcement

**Server-side (security):**
- Data URL format: `^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$`
- Data URL length: max 500,000 chars (~375KB decoded)

### Error Handling

| Layer | Error | Response |
|-------|-------|----------|
| Frontend validation | Invalid file type | Toast: "Please upload an image (JPEG, PNG, or WebP)" |
| Frontend validation | File too large | Toast: "Image must be under 10MB" |
| Backend validation | Invalid data URL format | 400: "Invalid image data format" |
| Backend validation | Data URL too large | 400: "Image data too large" |
| Backend | Database error | 500: "Could not save photo" |

---

## 4. Implementation Order

### Phase 1: Dependencies & Schema
1. [ ] `package.json`: Add `cropperjs@^2.0.0` dependency
2. [ ] `database.py:init_db()`: Add migration for `photo` column
3. [ ] `schemas.py`: Add `PhotoUpload`, `PhotoResponse` schemas; update `PersonalInfo`

### Phase 2: Backend API
4. [ ] `routes/photos.py`: Create router with GET, PUT, DELETE endpoints
5. [ ] `routes/__init__.py` or `main.py`: Register photos router
6. [ ] `tests/test_photos.py`: Write API tests

### Phase 3: Frontend API
7. [ ] `src/lib/api.js`: Add `getPhoto()`, `uploadPhoto()`, `deletePhoto()` functions

### Phase 4: UI Components
8. [ ] `src/components/PhotoUpload.svelte`: Create upload zone component
9. [ ] `src/components/PhotoEditor.svelte`: Create editor modal with Cropper.js
10. [ ] `src/components/PersonalInfo.svelte`: Integrate PhotoUpload component

### Phase 5: Integration Testing
11. [ ] Manual testing: Upload, crop, rotate, zoom, apply, delete flows
12. [ ] Run `pytest` to verify all tests pass

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Cropper.js v2 web components don't render in Svelte | Low | Med | Use `onMount` with dynamic import; web components are framework-agnostic |
| Base64 too large for SQLite TEXT | Low | Low | 400x400 JPEG at 85% is ~50-150KB; TEXT has no practical limit |
| Cropper.js CSS conflicts with app styles | Low | Low | Scope styles in PhotoEditor component |
| Browser compatibility for web components | Low | Low | Modern browsers (Chrome, Firefox, Safari, Edge) all support custom elements |

---

## 6. API Contract

### GET /api/photos
Returns current photo data URL or null.

**Response 200:**
```json
{
  "image_data": "data:image/jpeg;base64,..."
}
```
**Response 200 (no photo):**
```json
null
```

### PUT /api/photos
Upload or replace photo.

**Request:**
```json
{
  "image_data": "data:image/jpeg;base64,..."
}
```
**Response 200:**
```json
{
  "image_data": "data:image/jpeg;base64,..."
}
```
**Response 400:**
```json
{
  "detail": "Invalid image data format"
}
```

### DELETE /api/photos
Delete photo.

**Response 204:** No content
**Response 404:** Photo not found

---

## 7. Component Specifications

### PhotoUpload.svelte

**Props:**
- `photo: string | null` - Current photo data URL
- `onPhotoChange: (dataUrl: string | null) => void` - Callback when photo changes

**State:**
- `isDragOver: boolean` - Drag-over visual feedback
- `showEditor: boolean` - Editor modal visibility
- `pendingFile: File | null` - File waiting to be edited

**Behavior:**
- Empty state: Shows upload zone (dashed circle, camera icon)
- Has photo: Shows circular photo with hover overlay (Change/Delete buttons)
- Drag-over: Visual feedback on zone
- File selection: Validates type/size, opens editor if valid, shows toast if invalid
- Delete: Opens ConfirmDialog (existing component), calls `onPhotoChange(null)`

### PhotoEditor.svelte

**Props:**
- `file: File` - Image file to edit
- `onApply: (dataUrl: string) => void` - Callback with processed image
- `onCancel: () => void` - Callback to close without saving

**State:**
- `loading: boolean` - Image loading state
- `saving: boolean` - Processing/saving state

**Behavior:**
- Modal with Cropper.js web components
- Fixed 1:1 aspect ratio with 3x3 grid overlay
- Rotate button (90° clockwise)
- Zoom slider (controlled via cropper methods)
- Reset button
- Circular preview panel
- Apply: Export 400x400 canvas → JPEG base64 → call `onApply`
- Cancel: Close modal, discard changes

---

*Next: /v4-checklist*
