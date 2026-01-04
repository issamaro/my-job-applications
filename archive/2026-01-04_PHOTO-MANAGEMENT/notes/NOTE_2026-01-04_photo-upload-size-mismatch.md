# Note: Photo Upload Size Validation Mismatch

**Date:** 2026-01-04
**Category:** LEARNING
**During:** Bug fix (post-PhotoEditor removal)

---

## What Happened

Photo upload feature broke after removing the PhotoEditor component. Users received "Could not save photo. Please try again." error when attempting to upload any reasonably-sized photo.

## Context

- **File(s):** `schemas.py`, `src/components/PhotoUpload.svelte`
- **Expected:** Photos up to 10MB should upload successfully
- **Actual:** Backend rejected all photos over ~375KB (500KB base64 limit)

---

## Resolution

The root cause was a validation mismatch:

| Layer | Limit | Notes |
|-------|-------|-------|
| Frontend | 10MB raw file | `PhotoUpload.svelte:15` |
| Backend | 500KB base64 | `schemas.py:332` |

The removed PhotoEditor component had been **compressing images client-side** before upload, keeping them under the backend limit. Without it, raw images exceeded the 500KB schema validation.

**Fix:** Increased backend limit from `500_000` to `15_000_000` bytes to accommodate base64-encoded 10MB files (base64 adds ~33% overhead).

```python
# schemas.py - PhotoUpload validator
# Before:
if len(v) > 500_000:

# After:
# 10MB file becomes ~13.3MB as base64, allow 15MB for safety
if len(v) > 15_000_000:
```

---

## Impact

- **Immediate:** Photo upload now works without client-side compression
- **Future:** N - Current fix is adequate for profile photos
- **Checklist:** N - One-time fix, not recurring pattern

---

## Lesson Learned

When removing a component that processes data before API calls, check if the backend validation was tuned to that processed output rather than raw input.

---

*Captured during photo-management implementation*
