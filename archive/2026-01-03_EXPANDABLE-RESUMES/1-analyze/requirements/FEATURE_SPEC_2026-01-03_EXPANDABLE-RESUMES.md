# Feature Spec: My Job Applications (Unified View)

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Fix the confusing UX where "Saved Job Descriptions" and "History" show related but disconnected information. Merge into one unified "My Job Applications" section with expandable resumes.

### Pain Point

**Current State (Broken Mental Model):**

```
+-- Saved Job Descriptions -------------------------+
|  "Untitled Job"                                   |
|  1 resume  <-- Can't click to see which resume   |
+---------------------------------------------------+

+-- History ----------------------------------------+
|  "Software Developer - R&D · Odoo"  <-- Same job |
|  Match: 72%                                       |
+---------------------------------------------------+

User: "Are these the same thing? Why two sections?"
```

**Problems identified:**
1. **Disconnected data** - Same job appears in two places with different names
2. **No navigation** - "1 resume" is just text, not clickable
3. **Broken linkage** - Clicking "Generate" from a saved JD creates a NEW JD instead of linking to existing
4. **Title confusion** - Saved JD shows "Untitled Job", History shows extracted "Software Developer at Odoo"

### User Persona

**Job Seeker** using the resume generator who:
- Has saved multiple job descriptions for applications they're tracking
- Has generated one or more tailored resumes from those JDs
- Wants to quickly find and access resumes for a specific job application
- Expects one job = one place to find all related resumes

---

## 2. BDD Scenarios

```gherkin
Feature: My Job Applications (Unified View)
  As a job seeker
  I want one unified section showing jobs and their resumes
  So that I can easily navigate my job applications

  # === UNIFIED VIEW ===

  Scenario: View my job applications
    Given I have generated resumes for 3 different jobs
    When I view the Resume Generator page
    Then I see one section called "My Job Applications"
    And each job shows its title, preview, date, and resume count
    And the most recent job is EXPANDED showing its resumes
    And older jobs are COLLAPSED

  Scenario: No separate History section
    Given I am on the Resume Generator page
    Then there is NO separate "History" section
    And all resumes are accessible only through "My Job Applications"

  Scenario: Empty state
    Given I have no saved job descriptions
    When I view "My Job Applications"
    Then I see "No job applications yet"
    And I see a hint: "Paste a job description above to get started."

  # === EXPAND/COLLAPSE ===

  Scenario: Most recent job auto-expanded
    Given I have 3 job applications
    When the page loads
    Then the first (most recent) job is expanded
    And I can see its resumes immediately
    And the other 2 jobs are collapsed

  Scenario: Expand a collapsed job
    Given a job is collapsed showing "2 resumes"
    When I click the expand toggle
    Then the job expands to show its resumes
    And resumes are sorted newest first
    And I see each resume's date and match score

  Scenario: Collapse an expanded job
    Given a job is expanded showing resumes
    When I click the collapse toggle
    Then the resume list hides
    And only the job summary remains visible

  Scenario: Job with no resumes has no toggle
    Given a job has 0 generated resumes
    Then the expand toggle is NOT shown
    And "0 resumes" is displayed as plain text

  # === RESUME ACCESS ===

  Scenario: Click resume to view
    Given a job is expanded showing resumes
    When I click on a resume item
    Then that resume loads in the preview panel
    And I can view and export it

  Scenario: Delete resume from expanded list
    Given a job is expanded showing 2 resumes
    When I click Delete on a resume
    Then I see a confirmation dialog "Delete Resume?"
    When I confirm
    Then the resume is deleted
    And the job now shows "1 resume"
    And the deleted resume is removed from the list

  # === LINKAGE FIX ===

  Scenario: Generate from loaded job links correctly
    Given I have a saved job titled "Untitled Job"
    And I load that job into the editor
    When I click "Generate Resume"
    Then the resume is linked to the SAME job (not a new one)
    And the job title updates to match the LLM-extracted title
    And the job's resume count increases by 1

  Scenario: Generate preserves custom title
    Given I have renamed a saved job to "Dream Job at Google"
    And I load that job into the editor
    When I click "Generate Resume"
    Then the job title stays "Dream Job at Google" (custom titles preserved)
    And the resume is linked to that job

  Scenario: Generate with no loaded job creates new
    Given I have NOT loaded any saved job
    And I paste a new job description
    When I click "Generate Resume"
    Then a new job is created automatically
    And the resume is linked to that new job

  # === SORTING ===

  Scenario: Jobs sorted by most recently updated
    Given I have jobs updated on Jan 1, Jan 2, Jan 3
    When I view "My Job Applications"
    Then the Jan 3 job appears first
    And the Jan 1 job appears last

  Scenario: Resumes sorted within job
    Given a job has resumes created Jan 1, Jan 2, and Jan 3
    When I expand the job
    Then the Jan 3 resume appears first
    And the Jan 1 resume appears last
```

---

## 3. Requirements

### Must Have (MVP)

**A. Merge Sections into "My Job Applications"**
- [ ] Remove `ResumeHistory` component from `ResumeGenerator.svelte`
- [ ] Rename section header "Saved Job Descriptions" → "My Job Applications"
- [ ] Sort jobs by `updated_at` DESC (most recent first)
- [ ] Auto-expand first job on page load

**B. Expandable Resume List in Job Item**
- [ ] Add expand/collapse toggle to `SavedJobItem` (only if `resume_count > 0`)
- [ ] Fetch resumes via `getJobDescriptionResumes(id)` when expanding
- [ ] Display each resume: date, match score, delete button
- [ ] Click resume to load in preview (reuse existing `onSelect` pattern)
- [ ] Delete resume with confirmation dialog

**C. Fix JD-Resume Linkage (Backend)**
- [ ] Modify `/resumes/generate` to accept optional `job_description_id`
- [ ] If `job_description_id` provided: link new resume to existing JD
- [ ] If not provided: create new JD (current behavior)
- [ ] Auto-update JD title from LLM result only if current title is "Untitled Job"

**D. Fix JD-Resume Linkage (Frontend)**
- [ ] Track `loadedJobId` in `ResumeGenerator` when user loads a saved JD
- [ ] Pass `loadedJobId` to generate API call
- [ ] Clear `loadedJobId` when user clears editor or pastes new text

**E. Delete Legacy Components**
- [ ] Delete `ResumeHistory.svelte`
- [ ] Delete `_history.scss` (or inline needed styles)

### Should Have (Enhancement)

- [ ] Cache expanded resumes (don't re-fetch on collapse/expand)
- [ ] Loading spinner while fetching resumes on expand
- [ ] Animate expand/collapse transition

### Won't Have (Out of Scope)

- **Inline resume preview** - Just load in main preview panel
- **Compare resumes side-by-side** - Different feature
- **Merge duplicate JDs** - Manual cleanup if needed
- **Drag to reorder** - Not needed

---

## 4. Data Already Available

### Backend Endpoints (Already Exist)

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `GET /job-descriptions` | List all jobs with resume_count | Already used by SavedJobsList |
| `GET /job-descriptions/{id}/resumes` | Get resumes for a job | Exists, unused by frontend |
| `DELETE /resumes/{id}` | Delete a resume | Already used by ResumeHistory |

### Frontend API (Already Exists)

| Function | Location | Notes |
|----------|----------|-------|
| `getJobDescriptionResumes(id)` | `api.js:219` | Returns `ResumeHistoryItem[]` |
| `deleteResume(id)` | `api.js:159` | Already implemented |

### Schema (Response)

```typescript
// ResumeHistoryItem (from backend)
{
  id: number,
  job_title: string,
  company_name: string,
  match_score: number,
  created_at: string  // ISO datetime
}
```

---

## 5. Assumptions

| Assumption | Category | Confidence | Risk if Wrong |
|------------|----------|------------|---------------|
| `GET /job-descriptions/{id}/resumes` returns correct linked resumes | Architecture | High | Would show wrong resumes |
| Resume IDs from `/job-descriptions/{id}/resumes` work with `getResume(id)` | Architecture | High | Resume selection would break |
| Existing `onSelect` pattern in ResumeHistory can be reused | UX | High | Minor refactor needed |
| LLM always extracts job_title and company_name | Architecture | High | Title update might be blank |
| Only expand toggle needed (not full accordion) | UX | High | Simpler implementation |

---

## 6. Open Questions

None - design is fully specified.

---

## 7. Technical Notes

### Files to Modify

| File | Change |
|------|--------|
| `src/components/ResumeGenerator.svelte` | Remove ResumeHistory, track loadedJobId |
| `src/components/SavedJobsList.svelte` | Rename to JobApplicationsList, auto-expand first |
| `src/components/SavedJobItem.svelte` | Add expandable resume list with fetch/delete |
| `src/components/ResumeHistory.svelte` | **DELETE** |
| `routes/resumes.py` | Accept optional job_description_id in generate |
| `schemas.py` | Update ResumeGenerateRequest schema |
| `services/resume_generator.py` | Link to existing JD, update title logic |

### Implementation Order

1. **Backend first** - Add `job_description_id` support (safe, additive)
2. **Expandable resumes** - Add to SavedJobItem
3. **Linkage** - Track and pass loadedJobId in frontend
4. **Delete History** - Only after expandable resumes work
5. **Rename** - Cosmetic changes last

---

*Next: /v3-ux*
