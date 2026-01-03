# Retrospective: PDF Export

**Date:** 2026-01-03
**Duration:** Single session

---

## 1. What Worked Well

### Planning
- **Scope decision was accurate** - 0/6 on size indicators correctly identified this as a single feature
- **Clear boundaries** - "Input (resume JSON) → Output (PDF)" framing kept scope tight
- **Library research upfront** - Context7 lookup for WeasyPrint/Jinja2 syntax prevented trial-and-error

### Implementation
- **HTML+CSS approach** - Same templates work for browser preview AND PDF generation
- **Lazy WeasyPrint import** - Loading inside `generate_pdf()` avoided startup issues with library path
- **Existing patterns** - Following established project conventions (FastAPI routes, Svelte 5 runes) made integration smooth

### Testing
- **94-point checklist** - Comprehensive verification contract caught details upfront
- **TestClient for API tests** - Quick, reliable endpoint testing without running server
- **Parallel test structure** - Unit tests (generator) and API tests (endpoint) are independent

### Tooling
- **Context7 library lookups** - Got correct syntax patterns for WeasyPrint, Jinja2, Pydantic v2
- **v3 workflow artifacts** - Each phase built on previous, creating clear traceability

---

## 2. What Could Improve

### Blockers
- **WeasyPrint system dependency** - Required `DYLD_FALLBACK_LIBRARY_PATH` on macOS
  - Not immediately obvious from pip install
  - Caused initial import failure

### Rework
- **PdfPreview.svelte Svelte syntax** - Initial `{#if}` blocks incorrectly wrapped tag boundaries
  - Required fix during inspection phase
  - Could have been caught with stricter template validation

### Gaps
- **No README update** - Environment requirement (library path export) not documented
  - User needs to know this for local development
  - Should add to project setup instructions

---

## 3. Assumption Review

| Assumption | Correct? | When Discovered | Impact |
|------------|----------|-----------------|--------|
| PDF generation happens on backend | ✅ Yes | Planning | Clean separation, API returns bytes |
| WeasyPrint for HTML+CSS to PDF | ✅ Yes | Planning | Works well, good CSS support |
| No page limit enforcement | ✅ Yes | Analysis | Kept scope manageable for MVP |
| Browser handles file download natively | ✅ Yes | Build | Standard blob/anchor pattern works |
| Templates are backend-defined | ✅ Yes | Build | Jinja2 FileSystemLoader works well |
| Live preview matches PDF exactly | ⚠️ Partial | Build | Close but browser rendering differs slightly from WeasyPrint |

### Key Insights
- **Browser vs WeasyPrint rendering** - While using same HTML/CSS, minor differences exist (e.g., font metrics). For MVP this is acceptable; future work could use iframe with actual PDF preview.
- **System dependencies matter** - WeasyPrint's reliance on Pango/Cairo means environment setup is non-trivial.

---

## 4. Lessons Learned

### 1. Document Environment Requirements Early
**Context:** WeasyPrint required `DYLD_FALLBACK_LIBRARY_PATH` on macOS, discovered during testing
**Action:** Add environment requirements to LIBRARY_NOTES and README during research phase

### 2. Lazy Import for Heavy Libraries
**Context:** WeasyPrint import failed at module load without library path
**Action:** Use lazy imports (inside function) for libraries with system dependencies

### 3. Svelte Template Boundaries
**Context:** `{#if}` blocks split across HTML tag boundaries caused syntax errors
**Action:** Keep conditional blocks entirely inside or outside tags, never split

### 4. ATS-Friendly = Simple
**Context:** ATS compatibility meant avoiding fancy CSS (columns, tables, custom fonts)
**Action:** Simpler templates are actually better for this use case

---

## 5. Process Feedback

| Phase | Rating | Notes |
|-------|--------|-------|
| /v3-scope | ★★★★★ | Size indicators correctly identified single feature |
| /v3-analyze | ★★★★★ | BDD scenarios covered all edge cases |
| /v3-plan | ★★★★★ | Library research prevented syntax issues |
| /v3-build | ★★★★☆ | Minor Svelte syntax issue caught in inspect |
| /v3-ship | ★★★★★ | Clean closure with proper commit |

### Suggested Improvements
- **Add environment check to checklist** - Verify system dependencies (brew, library paths) as Section 0 item
- **Template syntax linting** - Could add Svelte linter step to prevent syntax issues

---

## 6. Metrics

| Metric | Value |
|--------|-------|
| Files Created | 10 |
| Files Modified | 6 |
| Lines Added | ~1,450 |
| Tests Added | 20 |
| Total Tests | 79 |
| Checklist Points | 94 |

---

## Summary

**Overall:** Clean feature delivery with minor environment friction; HTML+CSS approach for PDF was the right choice.

**Top Lesson:** Document system dependencies (library paths, brew packages) during research phase, not during debugging.

---

*Retrospective Complete - Feature Shipped*
