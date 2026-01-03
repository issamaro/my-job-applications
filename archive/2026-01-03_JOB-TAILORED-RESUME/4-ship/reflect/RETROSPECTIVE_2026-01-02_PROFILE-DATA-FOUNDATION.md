# Retrospective: Profile Data Foundation

**Date:** 2026-01-02
**Feature:** Profile Data Foundation
**Duration:** Single session

---

## What Worked Well

### 1. Ecosystem Setup with uv + nvm
- Using `uv` for Python made version pinning and venv creation fast and reliable
- `.nvmrc` + `.npmrc` with `engine-strict=true` ensures Node version consistency
- Clear separation: `.python-version` for Python, `.nvmrc` for Node

### 2. Library Research Phase
- Looking up Pydantic v2 and Svelte 5 syntax upfront prevented deprecated pattern usage
- LIBRARY_NOTES became a reliable reference during implementation
- Version constraints copied directly to manifests ensured compatibility

### 3. Checklist-Driven Implementation
- Having explicit verification points (UX text, syntax patterns, a11y requirements) made implementation deterministic
- No guessing about empty state text or error messages
- Accessibility requirements were clear from the start

### 4. Test-First Database Setup
- Using temp file per test (`tempfile.mkstemp`) solved SQLite in-memory isolation issues
- FastAPI TestClient with Starlette made API testing straightforward
- 35 tests provided confidence for rapid iteration

### 5. Svelte 5 Runes
- `$state()`, `$derived()`, `$effect()` are cleaner than Svelte 4's magic
- `onclick={}` instead of `on:click={}` is more intuitive
- Component binding with `bind:this` worked well for parent-child communication

---

## What Could Be Improved

### 1. Frontend Testing
- No automated frontend tests (only manual inspection)
- Could add Playwright or Cypress for E2E testing
- Component tests with @testing-library/svelte would increase confidence

### 2. Error Handling Granularity
- Backend returns generic Pydantic validation errors
- Could improve with custom error messages per field
- Frontend shows "Could not save" without details

### 3. Form State Management
- Each component manages its own form state
- Could extract to a shared pattern or store
- Duplicate form validation logic in frontend and backend

### 4. Build Artifacts
- public/build/ is gitignored, so deployment requires build step
- Could consider committing build output for simpler deployment
- Or add CI/CD that builds on deploy

---

## Assumptions Reviewed

| Assumption | Correct? | Notes |
|------------|----------|-------|
| Svelte 5 is stable | YES | v5.46.1 worked without issues |
| SQLite is sufficient | YES | Single-user app, no concurrency needed |
| No ORM needed | YES | Direct sqlite3 was simpler for 5 tables |
| Auto-save only for Personal Info | YES | Explicit save for lists avoids accidental changes |
| Safari month input needs fallback | MAYBE | Fallback implemented but not tested on Safari |

---

## Lessons Learned

### 1. Always Activate Venv in Test Fixtures
The first test run failed because `database.DATABASE = ":memory:"` doesn't work with SQLite - each connection gets a fresh in-memory DB. Using temp files solved this.

### 2. Svelte 5 Requires Explicit Children Rendering
Unlike Svelte 4's `<slot/>`, Svelte 5 uses `{@render children()}`. Easy to miss if following older tutorials.

### 3. FastAPI Lifespan > on_event
`@app.on_event("startup")` is deprecated. Using `@asynccontextmanager` with `lifespan=` parameter is the modern approach.

### 4. Browser Extensions Can Cause Console Errors
Password managers and auto-fill extensions inject content scripts that may error on form focus. Testing in incognito/private mode confirms app is clean.

### 5. Engine-Strict Catches Version Mismatches Early
Adding `engine-strict=true` to `.npmrc` prevents installing with wrong Node version - good practice for team projects.

---

## Recommendations for Future Features

1. **Add E2E tests** before implementing multi-page or complex flows
2. **Consider form library** if forms become more complex (Superforms for SvelteKit)
3. **Add loading states** for individual API calls, not just initial load
4. **Implement optimistic updates** for better perceived performance
5. **Add error boundary** component for graceful failure handling

---

## Metrics

| Metric | Value |
|--------|-------|
| Files Created | 50 |
| Lines of Code | ~2,500 (app) + ~500 (tests) |
| Tests | 35 |
| Test Coverage | High (all API endpoints covered) |
| Build Time | <1s (Rollup) |
| Dependencies | 5 Python, 8 Node |

---

## Team Notes

N/A (solo implementation)

---

*Retrospective complete - lessons captured for future work*
