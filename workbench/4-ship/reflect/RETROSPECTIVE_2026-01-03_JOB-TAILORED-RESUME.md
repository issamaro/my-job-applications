# Retrospective: Job-Tailored Resume Generation

**Date:** 2026-01-03
**Duration:** 2026-01-02 → 2026-01-03 (2 days)

---

## 1. What Worked Well

### Planning
- **Checklist approach** - The 178-point checklist provided clear verification targets and prevented scope creep
- **Dependency research upfront** - LIBRARY_NOTES with exact version constraints prevented SDK version conflicts
- **UX design detail** - Having exact text, colors, and component specifications in UX_DESIGN eliminated ambiguity during implementation

### Implementation
- **Service layer architecture** - Separating llm.py, profile.py, and resume_generator.py made code testable and maintainable
- **Mocking the LLM** - Testing with mocked Anthropic responses allowed fast, reliable test execution
- **Svelte 5 runes** - $state(), $props(), $derived() patterns were consistent and predictable once established in Feature 1

### Testing
- **Test-first for API** - Writing endpoint tests before full implementation caught schema issues early
- **59 passing tests** - Comprehensive coverage gave confidence for refactoring

### Tooling
- **AsyncAnthropic client** - Clean integration with FastAPI's async model
- **Context7 research** - Up-to-date documentation lookup prevented outdated pattern usage

---

## 2. What Could Improve

### Blockers
- **LLM prompt iteration** - Getting reliable JSON output from Claude required several prompt refinements
- **SCSS organization** - 577 new lines in main.scss is getting unwieldy; should consider component-scoped styles

### Rework
- **Initial component structure** - First pass had ResumePreview doing too much; refactored to extract ResumeSection and RequirementsAnalysis

### Gaps
- **No E2E tests** - Manual browser testing was sufficient but automated Playwright tests would improve confidence
- **No API key validation** - App doesn't gracefully handle missing ANTHROPIC_API_KEY until first generation attempt

---

## 3. Assumption Review

| Assumption | Correct? | When Discovered | Impact |
|------------|----------|-----------------|--------|
| User has Anthropic API key | ✅ Yes | Build | Added .env.example template |
| Single-user system continues | ✅ Yes | Planning | No changes needed |
| LLM can extract structured data | ⚠️ Partial | Build | Required careful prompt engineering for consistent JSON |
| Profile data is sufficient | ✅ Yes | Build | Profile completeness check works well |
| English language only | ✅ Yes | Planning | Not tested with other languages |
| Text-only job descriptions | ✅ Yes | Planning | Works as designed |
| Resume output is structured data | ✅ Yes | Build | JSON structure enables section toggling |
| Generation takes < 30 seconds | ✅ Yes | Build | Claude Sonnet typically responds in 5-15 seconds |

### Key Insights
- LLM structured output reliability improved significantly with explicit JSON schema in prompt
- The profile completeness check (requiring work experience) prevents frustrating "garbage in, garbage out" scenarios

---

## 4. Lessons Learned

### 1. Prompt Engineering is Implementation Work
**Context:** Initially underestimated time for LLM prompt development; required multiple iterations to get consistent JSON output with match scoring logic
**Action:** In future LLM features, allocate explicit time for prompt iteration and include prompt versioning in the codebase

### 2. Component Extraction is Normal
**Context:** ResumePreview started as a single large component; needed to extract ResumeSection and RequirementsAnalysis for maintainability
**Action:** Start with working code, then extract when repetition or complexity appears (not premature abstraction)

### 3. Checklist Points Enable Parallel Work
**Context:** The 178 verification points allowed systematic progress tracking and clear "done" criteria
**Action:** Continue using detailed checklists for complex features; they're worth the upfront investment

### 4. Mock Early, Mock Well
**Context:** LLM mocking in tests allowed 59 tests to run in seconds rather than minutes/dollars
**Action:** Always design services with dependency injection for testability; create realistic mock responses

---

## 5. Process Feedback

| Phase | Rating | Notes |
|-------|--------|-------|
| /v3-scope | ⭐⭐⭐⭐⭐ | Correctly identified as single feature despite complexity |
| /v3-analyze | ⭐⭐⭐⭐⭐ | BDD scenarios + UX design provided complete blueprint |
| /v3-plan | ⭐⭐⭐⭐⭐ | Library research prevented SDK issues; checklist was comprehensive |
| /v3-build | ⭐⭐⭐⭐⭐ | Test/Inspect loop caught all issues before shipping |
| /v3-ship | ⭐⭐⭐⭐⭐ | Archive + commit process is clean |

### Suggested Improvements
- Consider adding a "prompt engineering" checkpoint for LLM features
- SCSS could benefit from component-level organization (future refactor)
- Add startup validation for required environment variables

---

## 6. Metrics

| Metric | Value |
|--------|-------|
| Files Created | 24 |
| Files Modified | 7 |
| Lines Added | ~6,700 |
| Tests Written | 24 new (59 total) |
| Checklist Points | 178 |
| Components Created | 9 |

---

## Summary

**Overall:** Feature 3 delivered smoothly with comprehensive test coverage and clean architecture. The v3 workflow provided clear milestones and prevented scope creep.

**Top Lesson:** LLM prompt engineering deserves dedicated implementation time and should be treated as code that requires iteration and testing.

---

*Retrospective Complete - Feature Shipped*
