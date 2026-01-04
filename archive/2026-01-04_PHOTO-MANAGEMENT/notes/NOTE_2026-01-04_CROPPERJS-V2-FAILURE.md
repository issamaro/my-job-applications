# Note: Cropper.js v2 Web Components Integration Failure

**Date:** 2026-01-04
**Category:** LEARNING
**During:** /v4-implement (Photo Management feature)

---

## What Happened

Cropper.js v2 web components (`cropper-canvas`, `cropper-image`, `cropper-selection`, `cropper-grid`) failed to work correctly despite multiple implementation attempts. The feature was ultimately removed rather than continue debugging.

## Context

- **File(s):** `src/components/PhotoEditor.svelte` (deleted)
- **Expected:** Functional photo cropping with zoom, pan, rotate, and real-time preview
- **Actual:** Multiple cascading failures:
  1. Preview never updated in real-time
  2. Zoom slider had no effect on image
  3. Reset button caused zoom instead of reset
  4. Grid overlay disappeared after styling changes
  5. `$toCanvas()` failed with "Could not save the photo" error

---

## Root Causes Identified

### 1. Zoom API Misunderstanding
- `$zoom(scale)` takes **percentage factors** (0.1 = +10%), not absolute values
- Formula `(newScale - lastScale) / lastScale` was correct but internal scale tracking was unreliable

### 2. Transform Matrix Complexity
- Initial transform from `$getTransform()` returns `[a, b, c, d, e, f]` matrix
- Image auto-scales to fit canvas, so initial scale !== 1.0
- Resetting to identity matrix `[1,0,0,1,0,0]` doesn't restore "fit to canvas" state

### 3. Event Handler Binding Issues
- Svelte 5 `onready`, `ontransform`, `onchange` on custom elements may not bind correctly
- Web components use different event dispatch mechanism than standard DOM

### 4. Undocumented Behaviors
- `cropper-grid` requires `role="grid"` attribute (not obvious from examples)
- `cropper-selection.$toCanvas()` silently fails under certain transform states

---

## Resolution

**Removed PhotoEditor.svelte entirely.** PhotoUpload.svelte now uploads images directly without cropping/editing.

```javascript
// Simplified direct upload (no editor)
async function uploadFile(file) {
  const dataUrl = await fileToDataUrl(file);
  await uploadPhoto(dataUrl);
  photo = dataUrl;
}
```

---

## Lessons Learned

1. **Cropper.js v2 web components are immature** - v1 jQuery-style API is more stable
2. **Test incrementally** - Should have tested zoom/reset/preview individually before combining
3. **Web components + Svelte 5** - Event binding needs explicit `addEventListener` for custom elements
4. **Transform matrices** - When library handles initial scaling, can't assume identity matrix as baseline

---

## Alternative Approaches for Future

| Approach | Pros | Cons |
|----------|------|------|
| Cropper.js v1 (classic) | Well-documented, stable | jQuery-style API |
| react-image-crop (via adapter) | Simple API | React dependency |
| Canvas API manual implementation | Full control | More code |
| Server-side cropping | Offload complexity | Requires backend changes |

---

## Impact

- **Immediate:** Photo upload works but without crop/edit functionality
- **Future:** YES - Add to backlog as separate refined item for photo editing
- **Checklist:** NO - Not a recurring pattern, specific to this library

---

*Captured during PHOTO-MANAGEMENT implementation*
