# Retrospective Insights: MyCV-2

**Purpose:** Consolidated lessons from all feature retrospectives
**Source:** 6 feature retrospectives from archive/

---

## Cross-Feature Patterns

### What Consistently Worked

1. **Checklist-Driven Development**
   - Detailed verification points (94-178 per feature) prevented scope creep
   - Clear "done" criteria made progress measurable
   - UX text, error messages, and a11y requirements defined upfront

2. **Library Research Phase**
   - Context7 lookups for current syntax prevented deprecated patterns
   - LIBRARY_NOTES became reliable reference during implementation
   - Version constraints copied directly to manifests

3. **Service Layer Architecture**
   - Separating routes/services/database made code testable
   - LLM mocking enabled fast, reliable tests
   - Clear boundaries simplified refactoring

4. **Test-First API Development**
   - Writing endpoint tests before implementation caught schema issues
   - Temp file per test solved SQLite isolation issues
   - TestClient made API testing quick

5. **Svelte 5 Runes**
   - `$state()`, `$derived()`, `$effect()` patterns were consistent
   - `onclick={}` more intuitive than `on:click={}`
   - No circular dependency issues in app code

---

## Lessons by Category

### Environment & Tooling

| Lesson | Source Feature | Recommendation |
|--------|---------------|----------------|
| `uv` + `nvm` for version pinning | Profile Data Foundation | Use `.python-version` + `.nvmrc` |
| `engine-strict=true` in .npmrc | Profile Data Foundation | Catches version mismatches early |
| Lazy import for heavy libraries | PDF Export | Import inside function, not module level |
| Document system deps early | PDF Export | Add to LIBRARY_NOTES during research |

### Frontend Development

| Lesson | Source Feature | Recommendation |
|--------|---------------|----------------|
| Svelte 5 uses `{@render children()}` | Profile Data Foundation | Not `<slot/>` from Svelte 4 |
| Keep `{#if}` inside or outside tags | PDF Export | Never split across tag boundaries |
| Component extraction is normal | Job-Tailored Resume | Start working, extract when needed |
| Browser extensions cause console errors | Profile Data Foundation | Test in private/incognito mode |

### Backend Development

| Lesson | Source Feature | Recommendation |
|--------|---------------|----------------|
| SQLite temp files, not `:memory:` | Profile Data Foundation | Each connection gets fresh in-memory DB |
| FastAPI lifespan > on_event | Profile Data Foundation | `@asynccontextmanager` is modern approach |
| Prompt engineering is implementation work | Job-Tailored Resume | Allocate time for LLM prompt iteration |
| Mock LLM early and well | Job-Tailored Resume | Design for dependency injection |

### Architecture

| Lesson | Source Feature | Recommendation |
|--------|---------------|----------------|
| HTML+CSS for PDF works well | PDF Export | Same templates for preview and export |
| ATS-friendly = simple CSS | PDF Export | Avoid columns, tables, custom fonts |
| Single source of truth | All | Profile data as foundation for everything |
| JSON structure enables UI flexibility | Job-Tailored Resume | Section toggling, reordering possible |

---

## Process Ratings (Average Across Features)

| Phase | Rating | Notes |
|-------|--------|-------|
| /v3-scope | 5.0/5 | Size indicators consistently accurate |
| /v3-analyze | 5.0/5 | BDD scenarios + UX design = complete blueprint |
| /v3-plan | 5.0/5 | Library research prevented all SDK issues |
| /v3-build | 4.8/5 | Minor syntax issues caught in inspection |
| /v3-ship | 5.0/5 | Archive + commit process is clean |

---

## Suggested Process Improvements

From retrospective "Could Improve" sections:

1. **Add E2E tests** - Playwright/Cypress for complex flows
2. **Component form library** - If forms become more complex
3. **Startup validation** - Check required env vars on boot
4. **Environment check in checklist** - Section 0 for system deps
5. **Svelte linter** - Prevent template syntax issues
6. **Prompt versioning** - Treat LLM prompts as code

---

## Metrics Trend

| Feature | Files | Lines | Tests | Duration |
|---------|-------|-------|-------|----------|
| Profile Data Foundation | 50 | ~3,000 | 35 | 1 session |
| Job-Tailored Resume | 31 | ~6,700 | 24 | 2 days |
| PDF Export | 16 | ~1,450 | 20 | 1 session |
| Saved Job Descriptions | 12 | ~800 | 17 | 1 session |
| Expandable Resumes | 8 | ~400 | 5 | 1 session |
| SCSS Refactor | 18 | ~600 | 0 | 1 session |

**Cumulative:**
- Total Tests: 101
- Total Source Files: 52
- Total Lines: ~12,000+

---

## Assumption Accuracy

Tracking assumption correctness across features:

| Assumption Pattern | Accuracy | Notes |
|-------------------|----------|-------|
| Stack choices (Python, Svelte, SQLite) | 100% | All worked as expected |
| Single-user system | 100% | No concurrency issues |
| LLM can extract structured data | 80% | Required prompt engineering |
| Browser rendering = PDF rendering | 60% | Minor differences acceptable |
| Safari month input fallback needed | Unknown | Implemented but not tested |

---

## Red Flags to Watch

Patterns that caused friction:

1. **Large single components** - ResumePreview needed extraction
2. **577+ lines in main.scss** - Needed modular refactor
3. **Missing env var validation** - App fails on first LLM call, not startup
4. **No README for system deps** - WeasyPrint setup not documented

---

*Insights consolidated for onboarding and future development*
