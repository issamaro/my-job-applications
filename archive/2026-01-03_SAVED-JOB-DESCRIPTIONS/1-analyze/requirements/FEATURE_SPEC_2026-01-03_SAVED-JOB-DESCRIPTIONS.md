# Feature Spec: Saved Job Descriptions

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Allow users to save and edit job descriptions. When a saved job description is modified, automatically regenerate the tailored resume with the updated input. Track version history for traceability.

### Pain Point

**Current State:**
- Job descriptions are stored in the database but hidden from users
- Users can only see generated resumes in history (by job title/company)
- No way to view or edit the original JD text after generation
- No way to refine a JD and regenerate without starting from scratch
- No traceability between JD edits and resulting resume changes

**User Impact:**
- Users copy/paste the same JD multiple times when iterating
- No way to make small corrections to a JD (fix typos, add details) without full re-paste
- Hard to compare resume outputs from slightly different JD inputs
- Work is lost if user wants to return to a previous JD version

### User Persona

**Primary:** Job Seeker using the resume generator
- Iterates on job descriptions to optimize match score
- Wants to track which version of a JD produced which resume
- May save multiple JDs for different target positions
- Values the ability to refine inputs and see immediate results

---

## 2. BDD Scenarios

```gherkin
Feature: Saved Job Descriptions
  As a job seeker
  I want to save and manage job descriptions
  So that I can iterate on my inputs and track resume versions

  # === SAVE JD ===

  Scenario: Save a job description while generating
    Given I am on the resume generator tab
    And I have pasted a valid job description
    When I click "Generate Resume"
    Then the job description is automatically saved
    And I can see it in my saved job descriptions list
    And it has a title derived from the job analysis (job_title at company_name)

  Scenario: Save a job description without generating
    Given I am on the resume generator tab
    And I have pasted a valid job description (100+ chars)
    When I click "Save Job Description"
    Then the job description is saved
    And I see a success message "Job description saved"
    And the JD appears in my saved list with title "Untitled Job"
    And no resume is generated yet

  # === LIST SAVED JDs ===

  Scenario: View saved job descriptions
    Given I have previously saved job descriptions
    When I view the saved job descriptions panel
    Then I see a list of saved JDs ordered by most recent first
    And each item shows: title, company (if known), date saved
    And I can expand an item to see the JD text preview (first 200 chars)

  Scenario: Empty state for saved JDs
    Given I have no saved job descriptions
    When I view the saved job descriptions panel
    Then I see "No saved job descriptions yet"
    And I see a hint: "Paste a job description above and click Save to keep it for later"

  # === SELECT SAVED JD ===

  Scenario: Load a saved JD into the editor
    Given I have saved job descriptions
    When I click on a saved JD item
    Then the JD text is loaded into the job description input
    And the "Generate Resume" button becomes active (if 100+ chars)
    And I can edit the text before generating

  # === EDIT JD ===

  Scenario: Edit and regenerate from saved JD
    Given I have loaded a saved JD into the editor
    And I make changes to the JD text
    When I click "Generate Resume"
    Then a new resume is generated with the updated JD
    And the saved JD is updated with the new text
    And a new version is recorded in the JD history
    And the old resume remains accessible in history

  Scenario: Edit saved JD title
    Given I have a saved JD
    When I click the edit icon next to the JD title
    Then I can type a new title
    When I press Enter or click away
    Then the title is saved
    And I see the updated title in the list

  # === DELETE JD ===

  Scenario: Delete a saved JD
    Given I have a saved JD with generated resumes
    When I click "Delete" on the JD
    Then I see a confirmation dialog
    And the dialog warns that associated resumes will be deleted
    When I confirm deletion
    Then the JD and all its generated resumes are removed
    And the JD no longer appears in my saved list

  Scenario: Cancel JD deletion
    Given I click "Delete" on a saved JD
    And I see the confirmation dialog
    When I click "Cancel"
    Then the JD is not deleted
    And I return to the normal view

  # === VERSION HISTORY ===

  Scenario: View JD version history
    Given I have a saved JD that has been edited multiple times
    When I click "Version History" on the JD
    Then I see a list of all versions with timestamps
    And I can see a diff/comparison between versions
    And each version shows which resume(s) were generated from it

  Scenario: Restore previous JD version
    Given I am viewing JD version history
    When I click "Restore" on a previous version
    Then that version's text is loaded into the editor
    And I can generate a new resume from it
    And the restore creates a new version (doesn't modify history)

  # === RESUME LINKING ===

  Scenario: View resumes linked to a JD
    Given I have a saved JD with multiple generated resumes
    When I expand the saved JD item
    Then I see a list of resumes generated from this JD
    And each resume shows: date, match score, version number
    And I can click a resume to view it

  # === VALIDATION ===

  Scenario: Save empty job description
    Given the job description input is empty
    When I click "Save Job Description"
    Then I see an error "Please enter a job description"
    And nothing is saved

  Scenario: Save too-short job description
    Given the job description has fewer than 100 characters
    When I click "Save Job Description"
    Then I see an error "Job description must be at least 100 characters"
    And nothing is saved

  # === ERROR HANDLING ===

  Scenario: Network error while saving
    Given I have entered a valid job description
    And the network is unavailable
    When I click "Save Job Description"
    Then I see an error "Could not save. Please try again."
    And the JD text remains in the input
```

---

## 3. Requirements

### Must Have (MVP)

- [ ] **Save JD independently** - Save button to store JD without generating
- [ ] **Auto-save on generate** - Generating a resume also saves/updates the JD
- [ ] **List saved JDs** - Panel showing all saved JDs with title, company, date
- [ ] **Load saved JD** - Click to populate editor with saved JD text
- [ ] **Delete saved JD** - Remove JD with confirmation (cascades to resumes)
- [ ] **Edit JD title** - Inline editing of JD title
- [ ] **Link resumes to JDs** - Show which resumes were generated from which JD
- [ ] **JD text preview** - Show truncated JD text in list view
- [ ] **Validation** - Enforce 100 char minimum before save

### Should Have (Enhancement)

- [ ] **Version history** - Track JD text changes over time
- [ ] **Version diff view** - Compare two JD versions side by side
- [ ] **Restore version** - Load previous JD version into editor
- [ ] **Resume count badge** - Show number of resumes per JD in list

### Won't Have (Out of Scope)

- **JD parsing/tagging** - No automatic keyword extraction or categorization
- **JD templates** - No pre-built JD templates to start from
- **JD sharing** - No export/import of JDs between users
- **Bulk operations** - No multi-select delete or bulk regenerate
- **Search/filter** - No search within saved JDs (list only)
- **JD duplicate detection** - No warning if saving similar JD

---

## 4. Data Model Changes

### SQLite Compliance Notes

1. **ALTER TABLE limitations**: SQLite ADD COLUMN doesn't support `DEFAULT CURRENT_TIMESTAMP` - use NULL default, then UPDATE
2. **CASCADE behavior**: Existing FK lacks ON DELETE CASCADE - handle deletion in application code
3. **Foreign keys**: Must enable with `PRAGMA foreign_keys = ON` in connection

### job_descriptions table updates

```sql
-- Current schema
CREATE TABLE job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    parsed_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- SQLite-compliant migrations (run in order)
ALTER TABLE job_descriptions ADD COLUMN title TEXT DEFAULT 'Untitled Job';
ALTER TABLE job_descriptions ADD COLUMN company_name TEXT;
ALTER TABLE job_descriptions ADD COLUMN updated_at TEXT;  -- No DEFAULT for timestamp
ALTER TABLE job_descriptions ADD COLUMN is_saved INTEGER DEFAULT 1;

-- Backfill updated_at for existing rows
UPDATE job_descriptions SET updated_at = created_at WHERE updated_at IS NULL;
```

### New table: job_description_versions (Should Have)

```sql
CREATE TABLE IF NOT EXISTS job_description_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_description_id INTEGER NOT NULL,
    raw_text TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
);

-- Note: ON DELETE CASCADE only works if PRAGMA foreign_keys = ON
```

### generated_resumes table - CASCADE handling

```sql
-- Existing FK (no cascade):
-- FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)

-- Option A: Recreate table with cascade (disruptive, requires data migration)
-- Option B: Handle cascade in application code (recommended for MVP)

-- We'll use Option B: Delete resumes manually before deleting JD
-- In routes/job_descriptions.py:
--   DELETE FROM generated_resumes WHERE job_description_id = ?
--   DELETE FROM job_descriptions WHERE id = ?

-- Add version reference (Should Have)
ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER;
```

### Database connection update required

```python
# In database.py get_db():
conn = sqlite3.connect(DATABASE)
conn.execute("PRAGMA foreign_keys = ON")  # Enable FK enforcement
conn.row_factory = sqlite3.Row
```

---

## 5. API Endpoints

### New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/job-descriptions` | List all saved JDs |
| POST | `/api/job-descriptions` | Save new JD (without generating) |
| GET | `/api/job-descriptions/{id}` | Get single JD with details |
| PUT | `/api/job-descriptions/{id}` | Update JD title or text |
| DELETE | `/api/job-descriptions/{id}` | Delete JD and associated resumes |
| GET | `/api/job-descriptions/{id}/resumes` | Get resumes linked to this JD |
| GET | `/api/job-descriptions/{id}/versions` | Get version history (Should Have) |
| POST | `/api/job-descriptions/{id}/versions/{version_id}/restore` | Restore version (Should Have) |

### Modified Endpoints

| Endpoint | Change |
|----------|--------|
| `POST /api/resumes/generate` | Accept optional `job_description_id` to use existing JD |

---

## 6. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| Single user system continues | Architecture | No multi-user JD isolation needed |
| SQLite handles cascading deletes | Architecture | Use FK ON DELETE CASCADE |
| JD text is plain text only | UX | No rich text formatting needed |
| Version history is linear | Architecture | No branching/merging of JD versions |
| Title auto-derived from LLM analysis | UX | job_title + company_name from generation |
| Max ~100 saved JDs typical | Architecture | No pagination needed for MVP |
| Existing resumes keep working | Architecture | Schema migration preserves data |

---

## 7. Open Questions (RESOLVED)

1. **Auto-regenerate on edit?** - Should editing a saved JD automatically trigger regeneration, or require explicit "Generate" click?
   - **Decision:** Require explicit user click (LLM calls are costly)

2. **Version history depth?** - How many versions to keep?
   - **Decision:** Keep all versions (storage is cheap for text)

3. **JD organization?** - Should users be able to organize JDs into folders/tags?
   - **Decision:** Out of scope for MVP

---

## 8. UI Components (Preview)

| Component | Purpose |
|-----------|---------|
| `SavedJobsList.svelte` | List of saved JDs with expand/collapse |
| `SavedJobItem.svelte` | Individual JD card with title, preview, actions |
| `JdVersionHistory.svelte` | Modal showing version timeline (Should Have) |
| `JobDescriptionInput.svelte` | **Modified** - Add "Save" button, load functionality |
| `ResumeGenerator.svelte` | **Modified** - Integrate saved JDs panel |

---

*Next: /v3-ux for detailed UX design*
