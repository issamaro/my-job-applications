# Feature Spec: Profile Data Foundation

**Date:** 2026-01-02
**Status:** Draft
**Parent Epic:** AI-RESUME-SYSTEM (Feature 1 of 5)

---

## 1. Problem Statement

### User Request
> Create the core data structure and UI to store professional experience as a single source of truth. Basic CRUD for personal info, work history, education, skills, projects.

### Pain Point
Users maintain multiple resume versions in scattered files, leading to:
- Inconsistent information across versions
- Lost updates when editing the wrong file
- No single authoritative source for professional history
- Manual copy-paste when creating new resume variants

### User Persona
**Job Seeker** - A professional who applies to multiple positions and needs to maintain accurate, up-to-date career information that can be tailored for different opportunities.

---

## 2. BDD Scenarios

```gherkin
Feature: Profile Data Foundation
  As a job seeker
  I want to enter my professional experience in one place
  So that I have a single source of truth for all my resume data

  # ============================================
  # PERSONAL INFO SCENARIOS
  # ============================================

  Scenario: Create personal info
    Given I am on the profile editor
    And I have no personal info saved
    When I enter my name, email, phone, location, and LinkedIn URL
    And I click save
    Then my personal info is persisted to storage
    And I see a success confirmation

  Scenario: Update personal info
    Given I have existing personal info saved
    When I change my phone number
    And I click save
    Then my updated info replaces the previous version
    And I see a success confirmation

  Scenario: Validation error on personal info
    Given I am editing my personal info
    When I leave the name field empty
    And I click save
    Then I see an error message "Name is required"
    And the form is not submitted

  # ============================================
  # WORK EXPERIENCE SCENARIOS
  # ============================================

  Scenario: Add first work experience
    Given I have no work experiences saved
    When I click "Add Work Experience"
    And I enter company, title, start date, end date, and description
    And I click save
    Then the work experience is added to my profile
    And it appears in the work experience list

  Scenario: Add multiple work experiences
    Given I have 2 work experiences saved
    When I add a third work experience
    Then I have 3 work experiences in my profile
    And they are displayed in reverse chronological order (newest first)

  Scenario: Edit existing work experience
    Given I have a work experience at "Acme Corp"
    When I click edit on that experience
    And I change the title from "Developer" to "Senior Developer"
    And I click save
    Then the work experience is updated
    And the list shows "Senior Developer"

  Scenario: Delete work experience
    Given I have a work experience at "Old Company"
    When I click delete on that experience
    And I confirm the deletion
    Then the experience is removed from my profile
    And it no longer appears in the list

  Scenario: Mark current position
    Given I am adding a work experience
    When I check "I currently work here"
    Then the end date field is disabled
    And the experience is saved without an end date

  # ============================================
  # EDUCATION SCENARIOS
  # ============================================

  Scenario: Add education entry
    Given I have no education entries
    When I click "Add Education"
    And I enter institution, degree, field of study, and graduation year
    And I click save
    Then the education entry is added to my profile

  Scenario: Edit education entry
    Given I have an education entry for "State University"
    When I change the degree from "BS" to "MS"
    And I click save
    Then the education entry is updated

  Scenario: Delete education entry
    Given I have an education entry
    When I delete it and confirm
    Then it is removed from my profile

  # ============================================
  # SKILLS SCENARIOS
  # ============================================

  Scenario: Add skills
    Given I have no skills saved
    When I enter "JavaScript, TypeScript, React"
    And I click save
    Then the skills are parsed and saved individually
    And they appear as separate skill tags

  Scenario: Remove a skill
    Given I have "JavaScript" in my skills
    When I click the remove button on "JavaScript"
    Then it is removed from my skills list


  # ============================================
  # PROJECTS SCENARIOS
  # ============================================

  Scenario: Add project
    Given I have no projects saved
    When I click "Add Project"
    And I enter name, description, technologies used, and optional URL
    And I click save
    Then the project is added to my profile

  Scenario: Edit project
    Given I have a project "Portfolio Website"
    When I update the description
    Then the project is updated in my profile

  Scenario: Delete project
    Given I have a project entry
    When I delete it and confirm
    Then it is removed from my profile

  # ============================================
  # PERSISTENCE SCENARIOS
  # ============================================

  Scenario: Data persists across sessions
    Given I have saved my complete profile
    When I close the application
    And I reopen it later
    Then all my profile data is still present

  Scenario: Auto-save while editing
    Given I am editing my work experience
    When I make changes
    Then my changes are auto-saved after a brief delay
    And I see an "auto-saved" indicator

  # ============================================
  # EDGE CASES
  # ============================================

  Scenario: Empty profile state
    Given I am a new user
    When I open the profile editor
    Then I see empty states for each section
    And I see prompts to add my first entry

  Scenario: Long text in description fields
    Given I am adding a work experience
    When I enter a 2000-character description
    Then the full description is saved
    And it displays properly with scrolling or expansion

  Scenario: Special characters in text
    Given I am saving my profile
    When I enter text with quotes, ampersands, and unicode
    Then the text is saved correctly without corruption
```

---

## 3. Requirements

### Must Have (MVP)
- [ ] **Database Schema:** SQLite tables for personal_info, work_experiences, education, skills, projects
- [ ] **API Endpoints:** FastAPI CRUD routes for each table
- [ ] **Personal Info CRUD:** Form to create/edit personal info (name, email, phone, location, LinkedIn, summary)
- [ ] **Work Experience CRUD:** Add, edit, delete work entries with company, title, dates, description, "current" flag
- [ ] **Education CRUD:** Add, edit, delete education entries with institution, degree, field, year
- [ ] **Skills CRUD:** Add, remove skills (name only, no proficiency in MVP)
- [ ] **Projects CRUD:** Add, edit, delete projects with name, description, technologies, URL
- [ ] **Validation:** Required field validation, date format validation
- [ ] **Delete Confirmation:** Confirm before deleting any entry
- [ ] **Desktop Layout:** Clean, usable interface

### Should Have (Enhancement)
- [ ] **Auto-save:** Save changes automatically after brief delay
- [ ] **Chronological Sorting:** Work and education sorted by date (newest first)
- [ ] **Rich Text for Descriptions:** Bullet points in work experience descriptions
- [ ] **Import from LinkedIn:** Parse LinkedIn profile export (nice to have)
- [ ] **Profile Completeness Indicator:** Show % complete to encourage filling all sections

### Won't Have (Out of Scope - Future Features)
- AI enhancement of profile entries (Feature 2)
- Job description matching/tailoring (Feature 3)
- PDF export (Feature 4)
- Application tracking (Feature 5)
- Multi-user / authentication
- Cloud sync / backup
- Resume templates or styling

---

## 4. Tech Stack (Confirmed)

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | Svelte + Rollup | Compiles to vanilla JS, minimal config |
| Styling | Dart Sass | Clean syntax, compiled at build time |
| Backend | Python + FastAPI | Minimal, async, serves API + static files |
| Database | SQLite (`app.db`) | Single file, ACID, built-in Python support |
| Testing | Pytest | Backend only for MVP |

**Config files (total: 4):**
- `package.json` — JS dependencies
- `rollup.config.js` — ~15 lines
- `requirements.txt` — Python dependencies
- `main.py` — FastAPI app

---

## 5. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| Svelte + Rollup | Tech Stack | Minimal bundler config. User confirmed. |
| SQLite storage | Architecture | Single file `app.db`. User confirmed. |
| Python FastAPI backend | Architecture | Serves API + static files. |
| Single user, local only | Architecture | No auth needed. |
| Standard 5 sections | UX | Personal Info, Work, Education, Skills, Projects. User confirmed. |
| Desktop-first | UX | Primary use on desktop. |
| Native HTML inputs | UX | `<input type="month">` for dates. No libraries. |
| No CSS framework | UX | Vanilla CSS with Sass. |

---

## 6. Open Questions

None. Stack confirmed.

---

## 7. Data Model (SQLite Schema)

```sql
-- Personal info (single row)
CREATE TABLE personal_info (
    id INTEGER PRIMARY KEY DEFAULT 1,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    linkedin_url TEXT,
    summary TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    CHECK (id = 1)  -- Enforce single row
);

-- Work experiences
CREATE TABLE work_experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- YYYY-MM
    end_date TEXT,             -- YYYY-MM, NULL if current
    is_current INTEGER DEFAULT 0,
    description TEXT,
    location TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Education
CREATE TABLE education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    graduation_year INTEGER,
    gpa REAL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Skills (name only for MVP, proficiency can be added later)
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    technologies TEXT,  -- Comma-separated or JSON array
    url TEXT,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

*Next: /v3-ux (this feature has UI changes)*
