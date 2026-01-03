# Retrospective: My Job Applications (Unified View)

**Date:** 2026-01-03
**Duration:** Single session

---

## 1. What Worked Well

### Planning
- **Detailed IMPL_PLAN with line numbers** - Having exact file:line references made implementation straightforward. Knew exactly where to make each change.
- **Phased approach** - Backend → Frontend → Delete legacy → Styles → Tests kept dependencies clear.
- **LIBRARY_NOTES** - Having correct Svelte 5 rune syntax documented prevented syntax errors.

### Implementation
- **Existing API already existed** - `getJobDescriptionResumes(id)` was already implemented, just needed to wire it up in the frontend.
- **Reusing patterns** - The delete confirmation dialog and loading state patterns from existing code made implementation faster.
- **Optional parameter approach** - Making `job_description_id` optional preserved backward compatibility with no breaking changes.

### Testing
- **New tests caught edge cases** - Writing tests for "title updates only if Untitled Job" confirmed the logic was correct.
- **Pre-existing failures clearly identified** - Knowing PDF tests fail due to missing system libs avoided confusion.

### Tooling
- **dev.sh script** - User pointed out the correct way to start the dev environment (better than manual uvicorn + npm).

---

## 2. What Could Improve

### Blockers
- **SCSS undefined variable** - Used `$spacing-sm` which doesn't exist in tokens. Should have checked available tokens before using variables.
- **Button nesting error** - Had `<button>` inside `<button>` which is invalid HTML. Svelte warned about this, requiring a restructure.

### Rework
- **SavedJobItem structure** - Had to restructure the component after the initial write to fix the button nesting. Should have considered HTML validity during initial design.

### Gaps
- **No SCSS token check in checklist** - The checklist verified Svelte 5 syntax but not SCSS token names. Could add a "SCSS variables exist" check.

---

## 3. Assumption Review

| Assumption | Correct? | When Discovered | Impact |
|------------|----------|-----------------|--------|
| `GET /job-descriptions/{id}/resumes` returns correct linked resumes | ✅ Yes | Implementation | API verified working |
| Resume IDs work with `getResume(id)` | ✅ Yes | Implementation | Selection works correctly |
| Existing `onSelect` pattern can be reused | ✅ Yes | Implementation | `handleSelectResume` followed same pattern |
| LLM always extracts job_title and company_name | ✅ Yes | Testing | Title update works correctly |
| Only expand toggle needed (not accordion) | ✅ Yes | UX Design | Multiple jobs can expand - simpler |

### Key Insights
- All assumptions held true, which indicates the analysis phase was thorough.
- The architecture was well-understood from the existing codebase exploration.

---

## 4. Lessons Learned

### 1. Check Available Design Tokens Before Writing SCSS
**Context:** Used `$spacing-sm` in new styles, but this token doesn't exist. Only `$spacing-grid`, `$spacing-section`, and `$spacing-field` are defined.
**Action:** Before writing new SCSS, read `_tokens.scss` to know what's available. Add token verification to the pre-implementation checklist.

### 2. Consider HTML Validity When Designing Component Structure
**Context:** Put a `<button>` inside another `<button>` for the expand toggle inside job-content. This is invalid HTML and Svelte warned about it.
**Action:** When designing clickable areas with nested interactions, use `<div>` with click handlers or restructure so buttons aren't nested. Check wireframe for clickable region conflicts.

### 3. Use Project Scripts, Not Manual Commands
**Context:** Tried to start frontend with `npm run dev` and serve with `http-server`, but project has `./dev.sh` that handles everything correctly.
**Action:** Check for existing shell scripts (`dev.sh`, `start.sh`, etc.) before manually starting servers.

---

## 5. Process Feedback

| Phase | Rating | Notes |
|-------|--------|-------|
| /v3-scope | ⭐⭐⭐⭐⭐ | Feature size was appropriate for single session |
| /v3-analyze | ⭐⭐⭐⭐⭐ | FEATURE_SPEC covered all scenarios, assumptions were accurate |
| /v3-plan | ⭐⭐⭐⭐⭐ | IMPL_PLAN with file:line refs was excellent for implementation |
| /v3-build | ⭐⭐⭐⭐☆ | Minor fixes needed (SCSS token, button nesting) |
| /v3-ship | ⭐⭐⭐⭐⭐ | Clean closure with comprehensive change log |

### Suggested Improvements

1. **Add SCSS token verification to CHECKLIST** - Section for "SCSS: Variables used exist in _tokens.scss"

2. **Add HTML validity check to UX_DESIGN** - When showing clickable regions, note which should be buttons vs divs to avoid nesting issues.

3. **Document project scripts in LIBRARY_NOTES Section 0** - Include `./dev.sh` or similar project-specific scripts alongside runtime requirements.

---

## Summary

**Overall:** Clean implementation of a UX consolidation feature. All assumptions held, backend changes were minimal and backward-compatible, frontend changes unified the experience.

**Top Lesson:** Always verify design tokens and HTML structure constraints before writing code - small oversights (undefined variable, nested buttons) cause friction during implementation.

---

*Retrospective Complete - Feature Shipped*
