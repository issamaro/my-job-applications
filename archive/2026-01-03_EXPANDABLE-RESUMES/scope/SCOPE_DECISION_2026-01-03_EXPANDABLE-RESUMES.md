# Scope Decision: My Job Applications (Unified View)

**Date:** 2026-01-03
**Classification:** Single Feature
**Re-evaluated:** 2026-01-03 (post UX design review)

---

## Request

> Fix the confusing UX where "Saved Job Descriptions" and "History" show related but disconnected information. Merge into one unified "My Job Applications" section.

## Context

The original request was to add expandable resumes to SavedJobItem. During analysis, we discovered deeper UX problems:

1. **Two sections showing related data** - "Saved JDs" and "History" confused users
2. **Title mismatch** - "Untitled Job" vs "Software Developer at Odoo" for same job
3. **Broken linkage** - Generate creates new JD instead of linking to existing
4. **No navigation** - Can't click "1 resume" to see it

**Solution:** Merge into one section called "My Job Applications" with expandable resumes.

---

## Size Indicators (Re-evaluated)

| Indicator | Status | Notes |
|-----------|--------|-------|
| Contains "and" connecting distinct capabilities | [x] | Merge + expand + linkage fix |
| Affects multiple user personas | [ ] | Single persona: job seeker |
| Spans multiple domains | [ ] | Single domain: job applications |
| Has multiple independent acceptance criteria | [x] | But all serve unified goal |
| User mentions phases or iterations | [ ] | No phasing requested |
| Would require > 10 files changed | [ ] | **9 files** (under threshold) |

**Indicators checked: 2** (borderline)

---

## Re-evaluation Analysis

### Could This Be Split?

| Potential Sub-feature | Standalone Value | Dependencies |
|-----------------------|------------------|--------------|
| A. Remove History section | Partial (simplifies UI) | None |
| B. Expandable resumes in SavedJobItem | Yes | Needs linkage fix (C) to be useful |
| C. Fix JD-Resume linkage | Yes | None |
| D. Auto-update JD title | Partial (cosmetic) | Tied to C |

### Why It Stays One Feature

1. **B depends on C** - Expandable resumes are useless if linkage is broken (would show wrong resumes)
2. **A + B are coupled** - Removing History requires moving its delete functionality into expandable resumes
3. **Net code reduction** - We're deleting 2 components (History + its styles), offsetting new code
4. **9 files < 10 threshold** - Within single feature bounds

### Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Takes longer than expected | Medium | Clear BDD scenarios = testable increments |
| Regression in History deletion | Low | Delete after expandable resumes work |
| Linkage fix breaks generation | Low | Backend change is additive (optional param) |

---

## Decision

**CONFIRMED: Single Feature**

Proceed as single feature because:

1. **Tightly coupled** - All changes serve one goal: unified job applications view
2. **Dependencies** - Expandable resumes require linkage fix to show correct data
3. **9 files** - Under 10 file threshold
4. **Net simplification** - Deleting History reduces overall complexity
5. **Clear acceptance criteria** - 12 BDD scenarios provide testable milestones

---

## Feature Name

**EXPANDABLE-RESUMES** (kept for artifact naming consistency)

---

## Files Affected (Final Count: 9)

| # | File | Change Type |
|---|------|-------------|
| 1 | `src/components/ResumeGenerator.svelte` | Modify (remove History) |
| 2 | `src/components/SavedJobsList.svelte` | Rename + modify (auto-expand) |
| 3 | `src/components/SavedJobItem.svelte` | Major modify (expandable resumes) |
| 4 | `src/components/ResumeHistory.svelte` | **DELETE** |
| 5 | `src/scss/views/_saved-jobs.scss` | Rename + modify |
| 6 | `src/scss/views/_history.scss` | **DELETE** |
| 7 | `backend/services/resume_generator.py` | Modify (accept JD id) |
| 8 | `backend/routes/resumes.py` | Modify (endpoint schema) |
| 9 | `backend/schemas.py` | Modify (request schema) |

---

## Implementation Order (Recommendation)

1. **Backend first** - Linkage fix (files 7-9)
2. **Frontend expand** - Add expandable resumes to SavedJobItem (file 3)
3. **Remove History** - Delete ResumeHistory after expand works (files 1, 4, 6)
4. **Rename** - Cosmetic rename of section/files (files 2, 5)

This order ensures each step is testable and rollback-safe.

---

*Re-evaluated: 2026-01-03 | Status: CONFIRMED SINGLE FEATURE*
