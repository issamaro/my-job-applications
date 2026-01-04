# Photo Management System - SCOPED_FEATURE

**Size:** M (Medium)
**Scoped:** 2026-01-04
**Files affected:** ~10-12
**Dependencies:** None
**Ready for:** /v4-feature

---

## Description

Add a complete photo management system for CV profile photos. Users can upload photos via drag-and-drop or file picker, then edit them using a dedicated modal with crop, rotate, and zoom controls. Photos are stored in the backend and displayed on the user's profile. Photos are also made available for templates that support them.

This feature provides the photo infrastructure. Templates that use photos (European templates) are a separate feature.

---

## Scope (IN)

### A. Photo Upload

- [ ] Drag-and-drop upload zone
- [ ] Click-to-upload file picker
- [ ] Accepts common image formats (JPEG, PNG, WebP)
- [ ] Client-side validation (file type, reasonable size limit)

### B. Photo Editor Modal

- [ ] Crop tool with fixed 1:1 square ratio and 3x3 grid overlay
- [ ] Rotate (90° steps)
- [ ] Zoom/scale control
- [ ] Real-time preview of final result
- [ ] Reset to original option
- [ ] Apply/Cancel actions

### C. Profile Display

- [ ] Photo displayed as circle on user profile page
- [ ] Circular placeholder when no photo is set
- [ ] Ability to edit/replace photo from profile

### D. Backend

- [ ] Photo upload endpoint (`POST /api/photos`)
- [ ] Photo update endpoint (`PUT /api/photos/{id}`)
- [ ] Photo delete endpoint (`DELETE /api/photos/{id}`)
- [ ] Photo retrieval endpoint (`GET /api/photos/{id}`)
- [ ] Photo processing (resize to reasonable max dimensions)
- [ ] Storage as base64 in database (SQLite compatible)

### E. Schema

- [ ] Add `photo` field to resume data model
- [ ] Photo stored as base64 data URI for PDF embedding

---

## Out of Scope (NOT)

- Template changes (handled in European Templates feature)
- AI-powered photo enhancement or background removal
- Multiple photos per resume
- External file storage (S3, etc.) - using database storage
- Fine rotation (only 90° steps)

---

## Success Criteria

- [ ] User can upload a photo via drag-and-drop or file picker
- [ ] Photo editor modal opens after upload
- [ ] User can crop photo with aspect ratio constraint
- [ ] User can rotate photo in 90° increments
- [ ] User can zoom/scale photo
- [ ] Preview updates in real-time during editing
- [ ] Edited photo persists across sessions (saved to backend)
- [ ] **Photo is visible on the user's profile page**
- [ ] Photo can be replaced or deleted
- [ ] Existing templates continue working (ignore photo field)

---

## Technical Notes

### Photo Editor Library

**Recommendation:** Cropper.js
- Mature, full-featured, touch support
- Well-documented
- Handles crop, rotate, zoom requirements

### Files to Create/Modify

| File | Change |
|------|--------|
| `backend/routes/photos.py` | NEW - Photo CRUD endpoints |
| `backend/services/photo_service.py` | NEW - Photo processing logic |
| `backend/schemas/resume.py` | Add `photo` field |
| `backend/models/resume.py` | Add `photo` column |
| `frontend/src/components/PhotoUpload.svelte` | NEW - Upload zone component |
| `frontend/src/components/PhotoEditor.svelte` | NEW - Cropper.js modal |
| `frontend/src/routes/profile/+page.svelte` | Display photo on profile |
| `frontend/src/lib/api.js` | Add photo API methods |
| `frontend/package.json` | Add cropperjs dependency |

### Storage Format

- Processed photo stored as base64 data URI
- Format: `data:image/jpeg;base64,{encoded_data}`
- Dimensions: 400x400px (square, displayed as circle)
- Quality: 85% JPEG (balance size/quality)

---

## Suggested Implementation Order

1. Backend schema + model changes
2. Photo service (processing logic)
3. Photo API endpoints
4. Frontend upload component
5. Frontend editor modal with Cropper.js
6. Profile page photo display
7. Integration + persistence

---

*Split from: `backlog/refined/european-cv-templates.md` (original XL)*
