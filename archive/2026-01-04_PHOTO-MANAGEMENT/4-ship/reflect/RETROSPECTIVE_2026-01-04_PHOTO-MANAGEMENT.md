# Retrospective: Photo Management

**Date:** 2026-01-04
**Feature:** Photo upload and storage for CV profile photos

---

## What Worked Well

### Planning
- Feature spec captured requirements clearly with BDD scenarios
- UX design aligned well with existing Personal Info layout
- Backend route design followed established patterns seamlessly

### Implementation
- Backend (routes/photos.py, schemas.py) was clean and straightforward
- PhotoUpload.svelte component is well-structured with proper accessibility
- Integration with PersonalInfo.svelte was minimal and clean
- Drag-and-drop + click-to-upload UX works smoothly

### Bug Diagnosis
- Root cause of upload failure (size limit mismatch) was identified quickly
- Fix was simple and effective (500KB → 15MB backend limit)

---

## What Could Improve

### Blockers
- **Cropper.js v2 web components integration failed** - Multiple issues with zoom, preview, and canvas export
- **Test framework dependency** - starlette/httpx version incompatibility blocked automated tests

### Rework
- Entire PhotoEditor component had to be removed after significant development time
- Had to pivot from "crop/edit" to "direct upload" mid-implementation

### Gaps
- Library evaluation was insufficient - should have created a standalone proof-of-concept before committing to Cropper.js v2
- Web components + Svelte 5 event binding wasn't validated upfront

---

## Assumption Review

| Assumption | Correct? | Impact |
|------------|----------|--------|
| Cropper.js is suitable for our needs | **No** | v2 web components proved unstable |
| 400x400px output is sufficient | Yes | Not tested (no server-side resize implemented) |
| Base64 storage is acceptable | Yes | Works well for single-user app |
| 85% JPEG quality is acceptable | N/A | Not implemented (frontend doesn't compress) |
| Single photo per user is sufficient | Yes | UX confirmed |
| Frontend handles initial file validation | Yes | Works correctly |
| Cropper.js works with Svelte 5 | **No** | Event binding issues with custom elements |

---

## Backlog Items Created

| Item | File | Priority |
|------|------|----------|
| Photo Editing Feature | `backlog/raw/photo-editing.md` | Medium |
| Test Dependency Fix | `backlog/raw/test-dependency-fix.md` | High |

---

## Process Feedback (v4 Workflow)

| Phase | Worked? | Notes |
|-------|---------|-------|
| /v4-scope | Yes | Clear refinement from raw backlog |
| /v4-analyze | Yes | Good spec, but library assumption wasn't validated |
| /v4-plan | Partial | Plan was solid but built on faulty library assumption |
| /v4-build | Yes | Implementation, test, inspect flow worked well |
| /v4-ship | Yes | Clean closure process |

---

## Summary

**Overall:** Feature delivered with reduced scope (upload only, no editing). Core value achieved but planned editing capability deferred.

**Top Lesson:** Validate third-party library integrations with a minimal proof-of-concept before committing to them in the implementation plan. Don't trust documentation alone, especially for newer APIs (web components).

---

*Retrospective Complete*
