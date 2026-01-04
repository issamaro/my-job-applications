# Change Log: Photo Management

**Date:** 2026-01-04
**Feature Spec:** FEATURE_SPEC_2026-01-04_PHOTO-MANAGEMENT.md
**Implementation Plan:** IMPL_PLAN_2026-01-04_PHOTO-MANAGEMENT.md

---

## Summary

Added photo upload capability for CV profile photos. Users can upload, replace, and delete photos via drag-and-drop or file picker. Photos are stored as base64 in the database and displayed on the profile page.

**Scope Note:** Photo editing (crop/rotate/zoom) was planned but removed due to Cropper.js v2 integration failures. Deferred to future backlog item.

---

## Files Added

### Backend
| File | Lines | Description |
|------|-------|-------------|
| routes/photos.py | 1-47 | Photo CRUD API endpoints (GET/PUT/DELETE) |
| tests/test_photos.py | 1-~150 | Photo API test suite |

### Frontend
| File | Lines | Description |
|------|-------|-------------|
| src/components/PhotoUpload.svelte | 1-352 | Photo upload component with drag-drop |

---

## Files Modified

### Backend
| File | Lines | Description |
|------|-------|-------------|
| main.py | 12, 32 | Import and register photos router |
| schemas.py | 324-338 | PhotoUpload and PhotoResponse schemas |
| database.py | (photo column) | Photo field in personal_info table |

### Frontend
| File | Lines | Description |
|------|-------|-------------|
| src/components/PersonalInfo.svelte | 3, 91 | Import PhotoUpload, add to layout |
| src/lib/api.js | 237-253 | Photo API functions (get/upload/delete) |

### Config
| File | Description |
|------|-------------|
| package.json | (no changes in final - cropperjs removed) |
| .env.example | (if any photo-related env vars) |

---

## Bug Fix Applied

| Issue | File | Change |
|-------|------|--------|
| Photo upload size mismatch | schemas.py:332 | Increased limit from 500KB to 15MB |

Backend validation was too restrictive (500KB) compared to frontend (10MB), causing "Could not save photo" errors after PhotoEditor removal.

---

## Checklist Verification

### Syntax Points (from CHECKLIST)
- [x] File validation → PhotoUpload.svelte:17-27
- [x] API endpoints → routes/photos.py:8-46
- [x] Schema validation → schemas.py:324-334

### UX Points (from CHECKLIST)
- [x] "Add profile photo" → PhotoUpload.svelte:183
- [x] "Drag or click" → PhotoUpload.svelte:184
- [x] "Drop to upload" → PhotoUpload.svelte:181
- [x] Error messages → PhotoUpload.svelte:19, 24, 72, 109
- [x] Delete confirmation → PhotoUpload.svelte:198

---

## Test Summary

| Category | Result |
|----------|--------|
| Photo API Tests | 11 tests (blocked by dependency issue) |
| Manual API Tests | All endpoints verified working |
| Frontend Build | Success |

Note: Pytest tests blocked by starlette/httpx version incompatibility (not code issue).

---

## Inspection Summary

| Category | Status |
|----------|--------|
| Browser Smoke | PASS |
| Accessibility | PASS |
| UX Match | PASS |

---

## Notes Captured

| Note | Description |
|------|-------------|
| NOTE_2026-01-04_CROPPERJS-V2-QUIRKS | Cropper.js v2 import patterns |
| NOTE_2026-01-04_CROPPERJS-V2-FAILURE | Decision to remove PhotoEditor |
| NOTE_2026-01-04_WEASYPRINT-SYSTEM-DEPS | WeasyPrint environment issue |
| NOTE_2026-01-04_photo-upload-size-mismatch | Backend size limit fix |

---

## Backlog Items Created

| Item | File |
|------|------|
| Photo Editing Feature | backlog/raw/photo-editing.md |
| Test Dependency Fix | backlog/raw/test-dependency-fix.md |

---

*Change Log Complete*
