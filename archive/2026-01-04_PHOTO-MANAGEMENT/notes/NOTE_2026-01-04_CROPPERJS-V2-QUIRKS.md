# Note: Cropper.js v2 Differences from Documentation

**Date:** 2026-01-04
**Category:** QUIRK / LEARNING
**During:** /v4-implement

---

## What Happened

Two unexpected behaviors with Cropper.js v2 that differed from the documented patterns in LIBRARY_NOTES.

---

## Finding 1: No Separate CSS File

### Context

- **File(s):** `src/components/PhotoEditor.svelte`
- **Expected:** Import CSS via `import 'cropperjs/dist/cropper.css'` (per LIBRARY_NOTES)
- **Actual:** File does not exist. Cropper.js v2 web components include their own styles via Shadow DOM.

### Resolution

Removed the CSS import entirely. Web components are self-contained.

```javascript
// Before (failed)
await import('cropperjs');
await import('cropperjs/dist/cropper.css');  // ENOENT error

// After (works)
import 'cropperjs';  // Web components auto-register with embedded styles
```

---

## Finding 2: Dynamic Import Incompatible with IIFE Build

### Context

- **File(s):** `src/components/PhotoEditor.svelte`, `rollup.config.js`
- **Expected:** Dynamic import `await import('cropperjs')` would work in onMount
- **Actual:** Rollup error: "UMD and IIFE output formats are not supported for code-splitting builds"

### Resolution

Changed from dynamic import to static import at module level.

```javascript
// Before (failed with IIFE build)
onMount(async () => {
  await import('cropperjs');
  // ...
});

// After (works)
import 'cropperjs';  // Static import at top of script

onMount(() => {
  // ...
});
```

---

## Root Cause

The LIBRARY_NOTES were based on Cropper.js v2 documentation patterns, but:

1. The CSS file path `cropperjs/dist/cropper.css` is from Cropper.js v1, not v2
2. The dynamic import pattern is standard but incompatible with this project's Rollup IIFE configuration

---

## Impact

- **Immediate:** Both issues resolved. PhotoEditor works correctly.
- **Future:** No - not a backlog item, just library knowledge
- **Checklist:** Yes - consider adding to PROJECT_CHECKS.md:
  - "Verify library import patterns match actual package structure"
  - "Check if dynamic imports are compatible with build configuration"

---

## Lessons for Future

1. **Always check `node_modules/{package}/dist/`** to verify actual file structure before documenting import paths
2. **Test build early** when adding new dependencies, especially with non-standard import patterns
3. **Cropper.js v2 uses web components** - they're self-contained (JS + CSS via Shadow DOM)

---

*Captured during PHOTO-MANAGEMENT implementation*
