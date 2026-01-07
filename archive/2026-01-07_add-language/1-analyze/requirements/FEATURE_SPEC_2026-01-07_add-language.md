# Feature Specification: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language
**Source:** `backlog/done/add-language.md`

## Problem Statement

### User Request (Capability)
Add a Languages section to the resume/CV application where users can list languages they speak along with their CEFR proficiency level.

### Pain Point (Problem)
Users currently have no way to include language skills on their CV, missing valuable information for international roles and positions requiring multilingual candidates.

### User Persona
**Job seeker managing their CV** - A resume creator who wants to showcase language skills to potential employers, particularly for roles that require or prefer multilingual candidates.

## BDD Scenarios

```gherkin
Feature: Language Section Management
  As a job seeker managing my CV
  I want to add languages with CEFR proficiency levels
  So that employers can see my language skills

  Scenario: Add a new language
    Given I am on the profile page
    When I click "Add Language"
    And I enter "French" as the language name
    And I select "B2" as the CEFR level
    And I save the entry
    Then I should see "French - B2" in my languages list
    And the language should persist in the database

  Scenario: Edit an existing language
    Given I have "Spanish - B1" in my languages list
    When I click edit on the Spanish entry
    And I change the level to "B2"
    And I save the changes
    Then I should see "Spanish - B2" in my languages list

  Scenario: Delete a language
    Given I have "German - A2" in my languages list
    When I click delete on the German entry
    And I confirm the deletion
    Then "German - A2" should no longer appear in my languages list

  Scenario: Reorder languages via drag-and-drop
    Given I have multiple languages in my list
    When I drag "French" above "English"
    Then "French" should appear before "English" in the list
    And the new order should persist

  Scenario: Invalid CEFR level rejected
    Given I am adding a new language via API
    When I submit a language with level "X1"
    Then the API should return a 422 validation error
    And the language should not be saved

  Scenario: Languages appear in resume preview
    Given I have languages in my profile
    And the Languages toggle is enabled
    When I view the resume preview
    Then I should see a Languages section
    And it should list my languages with their CEFR levels

  Scenario: Toggle languages section off
    Given I have languages in my profile
    When I toggle off the Languages section in resume preview
    Then the Languages section should not appear in the preview

  Scenario: Languages in PDF export
    Given I have languages in my profile
    And the Languages toggle is enabled
    When I export my resume to PDF
    Then the PDF should include a Languages section
    And it should display each language with its CEFR level code
```

## Requirements

### Must Have (MVP)
1. **Schema**: `Language` Pydantic schema with id, name, level (CEFR enum), display_order
2. **Database**: `languages` table with CRUD operations
3. **API**: RESTful endpoints at `/api/languages` (GET, POST, PUT, DELETE)
4. **Validation**: Backend validation rejecting non-CEFR levels
5. **Component**: `Languages.svelte` for profile page management
6. **Profile Integration**: Languages section on profile page
7. **Resume Generation**: Include languages in ResumeContent schema
8. **Resume Preview**: Display languages with toggle control
9. **PDF Export**: Languages section in both classic and modern templates
10. **Ordering**: Drag-and-drop reordering with persisted display_order

### Should Have
- CEFR level descriptions as tooltips in the input form (for user guidance when selecting)

### Won't Have (Out of Scope)
- Language flags/icons
- Native speaker designation (beyond C2)
- Language certificates (e.g., TOEFL, IELTS scores)
- Multiple proficiency types (speaking, reading, writing separately)
- AI/LLM matching of languages to job requirements

## Assumptions

| Assumption | Category | Status | Notes |
|------------|----------|--------|-------|
| Languages display in user-defined order via drag-and-drop | UX | Confirmed | User requested drag-and-drop for flexibility |
| Only CEFR level codes shown in output (not descriptions) | UX | Confirmed | Show "C2" not "C2 (Proficient)" in resume |
| Follow existing section patterns (Skills, Education) | Architecture | Assumed | Consistent codebase patterns |
| Use same ResumeSection wrapper component | Architecture | Assumed | UI consistency |
| Single database table with foreign key to user | Architecture | Assumed | Standard pattern |

## Open Questions

None - all assumptions validated.

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Primary user | A - Job seeker managing their CV | Persona focused on showcasing skills to employers |
| Pain point | A - Cannot include language skills on CV | Feature enables complete CV representation |
| Display order | User-defined via drag-and-drop | Added display_order field, drag-drop UX requirement |
| Level display | A - Codes only | Resume shows "B2" not "B2 (Upper Intermediate)" |
