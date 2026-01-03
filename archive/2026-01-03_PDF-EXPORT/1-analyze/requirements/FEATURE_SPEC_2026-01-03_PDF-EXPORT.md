# Feature Spec: PDF Export

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Problem Statement

### User Request

> Generate professional, ATS-friendly PDF resumes from the tailored resume output. Multiple template options, download functionality. This completes the MVP (Features 1+3+4).

### Pain Point

Currently, users can generate tailored resumes in the application, but they cannot export them as PDF files to send to recruiters. The resume preview is view-only within the app, making the entire system incomplete for real-world job applications.

### User Persona

Job seekers who have:
1. Entered their profile data (Feature 1)
2. Generated a tailored resume for a specific job (Feature 3)
3. Now need to download a professional PDF to submit with their application

---

## 2. BDD Scenarios

```gherkin
Feature: PDF Export
  As a job seeker
  I want to export my tailored resume as a PDF
  So that I can send it to recruiters and upload it to job application systems

  Scenario: Export resume with default template
    Given I have generated a tailored resume
    And I am viewing the resume preview
    When I click the "Download PDF" button
    Then a PDF file downloads to my computer
    And the filename is "[Name]_Resume_[Company].pdf"
    And the PDF contains all included resume sections

  Scenario: Export resume with different template
    Given I have generated a tailored resume
    And I am viewing the resume preview
    When I select the "Modern" template
    And I click the "Download PDF" button
    Then a PDF file downloads with the Modern template styling
    And the content matches my resume preview

  Scenario: Export resume with excluded sections
    Given I have generated a tailored resume
    And I have toggled off the "Projects" section
    When I click the "Download PDF" button
    Then the PDF does not contain the Projects section
    And all other included sections are present

  Scenario: PDF is ATS-friendly
    Given I have generated a tailored resume
    When I export it as PDF
    Then the PDF uses standard fonts (Arial, Helvetica, or Times New Roman)
    And all text is selectable (not embedded as images)
    And the PDF does not use tables for layout
    And the PDF does not use headers/footers that ATS may miss

  Scenario: Export while resume is loading
    Given a resume generation is in progress
    When I try to click "Download PDF"
    Then the button is disabled
    And it shows "Generating..." state

  Scenario: Export after editing description
    Given I have generated a tailored resume
    And I have edited a work experience description
    And the edit has been saved
    When I click "Download PDF"
    Then the PDF contains my edited description

  Scenario: No resume to export
    Given I am on the resume generator page
    And no resume has been generated yet
    Then the "Download PDF" button is not visible
```

---

## 3. Requirements

### Must Have

- [ ] Download PDF button on resume preview screen
- [ ] PDF generation from `ResumeContent` data structure
- [ ] Filename format: `[FullName]_Resume_[CompanyName].pdf`
- [ ] Include only sections marked as `included: true`
- [ ] ATS-friendly output:
  - [ ] Standard fonts (system fonts, no custom fonts)
  - [ ] Selectable text (no images of text)
  - [ ] Simple layout (no complex tables/columns)
  - [ ] Proper heading hierarchy
- [ ] At least 2 template options (Classic, Modern)
- [ ] Live template preview (exact match to downloaded PDF)
- [ ] Template selector UI with live preview
- [ ] Respect edited content (saved descriptions)
- [ ] Loading/disabled state during PDF generation

### Should Have

- [ ] Remember last selected template preference
- [ ] Success toast notification after download

### Won't Have

- [ ] Custom template builder (future feature)
- [ ] Cloud storage of PDFs (Feature 5 territory)
- [ ] Email/share functionality
- [ ] Hard page limit enforcement (needs more study for future)
- [ ] Cover letter generation

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| PDF generation happens on backend | Architecture | Frontend calls API, backend returns PDF bytes |
| WeasyPrint for HTML+CSS to PDF | Library | **DECIDED:** HTML+CSS approach for maintainability |
| No page limit enforcement | UX | **DECIDED:** MVP priority; page limits need future study |
| User has generated a resume before exporting | UX | Export button only visible after generation |
| Browser handles file download natively | Architecture | Use standard download response, no custom download UI |
| Templates are backend-defined | Architecture | Template HTML/CSS stored on server, not user-customizable |
| Live preview matches PDF exactly | UX | **DECIDED:** Same HTML/CSS renders in browser and PDF |

---

## 5. Resolved Questions

1. **Template implementation approach:** HTML+CSS rendered to PDF (WeasyPrint)
   - More maintainable and designer-friendly
   - Same CSS works for browser preview and PDF generation

2. **Template preview:** Live preview of each template
   - Must match exactly what gets downloaded
   - Same HTML/CSS template renders in both browser and WeasyPrint

3. **Page limit:** No hard enforcement for MVP
   - Focus on high-quality MVP first
   - Page limits need more study/flexibility for future iteration

---

## 6. Technical Notes

### Existing Data Structure

The `ResumeContent` schema (from `schemas.py`) contains:
- `personal_info`: dict (name, email, phone, location, linkedin)
- `summary`: str
- `work_experiences`: list[ResumeWorkExperience] (with `included` flag)
- `skills`: list[ResumeSkill] (with `included` flag)
- `education`: list[ResumeEducation] (with `included` flag)
- `projects`: list[ResumeProject] (with `included` flag)

### Existing API Pattern

Resume is fetched via `GET /api/resumes/{id}` returning `GeneratedResumeResponse`.

New endpoint needed: `GET /api/resumes/{id}/pdf?template=classic`

---

*Next: /v3-ux (UI changes required)*
