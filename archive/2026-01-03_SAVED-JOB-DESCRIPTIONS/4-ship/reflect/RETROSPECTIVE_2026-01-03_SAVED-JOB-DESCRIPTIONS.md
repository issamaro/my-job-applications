# Retrospective: Saved Job Descriptions

**Date:** 2026-01-03
**Feature:** Saved Job Descriptions

---

## What Went Well

### 1. Clear Requirements
The analyze phase produced well-structured REQUIREMENTS and UX_DESIGN documents that guided implementation without ambiguity.

### 2. Checklist-Driven Implementation
The 98-item CHECKLIST ensured nothing was missed. Each checklist item could be verified with a file:line reference.

### 3. Pattern Reuse
Successfully reused existing patterns:
- `ResumeHistory.svelte` → `SavedJobsList.svelte` (collapsible panel)
- `ConfirmDialog.svelte` (delete confirmation)
- SCSS token system (consistent spacing, colors)
- API client pattern (request helper)

### 4. PRAGMA foreign_keys Decision
Research identified the correct SQLite FK approach:
- Set PRAGMA in get_db() context manager
- Use ON DELETE CASCADE for new tables
- Hybrid approach for legacy FK without CASCADE

### 5. Test Coverage
17 new tests covering all API endpoints, validation, and cascade behavior. All passed on first run.

---

## What Could Be Improved

### 1. Nested Button Warning
Initial SavedJobItem implementation had buttons nested inside buttons (invalid HTML). Required refactoring during /v3-test phase.

**Lesson:** Review component structure for semantic HTML before building.

### 2. No Toast Integration
Implementation has `showToast` calls but the Toast component wasn't integrated in ResumeGenerator. The feature works but doesn't show toast notifications.

**Lesson:** Check existing toast/notification patterns early in implementation.

### 3. Version UI Deferred
Backend supports full version history but UI wasn't implemented. User can restore versions via API but not through the UI.

**Consideration:** Could have been a smaller MVP scope.

---

## Assumptions Review

| Assumption | Correct? | Notes |
|------------|----------|-------|
| SQLite FK enforcement needs PRAGMA | YES | Set on every connection |
| Users want to edit JD titles | YES | Inline editing pattern works well |
| Cascade delete is safe | YES | With confirmation dialog |
| 100 char minimum is appropriate | YES | Matches existing validation |

---

## Lessons Learned

### 1. Semantic HTML First
Always verify component structure for valid HTML nesting before implementation. Tools like Svelte warn at build time but fixing later requires refactoring.

### 2. SQLite FK Patterns
For SQLite:
- PRAGMA foreign_keys must be set on each connection
- ON DELETE CASCADE goes in FK definition
- Legacy FKs without CASCADE need manual delete

### 3. Component Composition
Breaking SavedJobsList into SavedJobsList + SavedJobItem made the code cleaner and more testable. Each component has a single responsibility.

### 4. Test Before Inspect
Running automated tests before manual inspection caught the nested button issue early, before it would have been harder to diagnose.

---

## Time Breakdown (Estimated)

| Phase | Proportion |
|-------|------------|
| Analyze | 15% |
| Plan | 20% |
| Build (Implement) | 45% |
| Build (Test + Inspect) | 15% |
| Ship | 5% |

---

## Recommendations for Future Features

1. **Run frontend build early** - Catch warnings before manual inspection
2. **Review semantic HTML** - Especially for interactive elements
3. **Check toast integration** - Ensure notification patterns are connected
4. **Scope version UI separately** - Backend-only version features are still useful

---

*Retrospective Complete*
