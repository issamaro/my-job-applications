# Implementation Plan: PDF Export

**Date:** 2026-01-03
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-03_PDF-EXPORT.md

---

## 1. Affected Files

### Config/Dependencies

| File | Change | Description |
|------|--------|-------------|
| `requirements.txt` | Modify | Add `weasyprint>=62.0`, `jinja2>=3.1.0` |

### Backend

| File | Change | Description |
|------|--------|-------------|
| `services/pdf_generator.py` | Create | PDF generation service with template rendering |
| `templates/resume_classic.html` | Create | Classic resume template (Jinja2) |
| `templates/resume_modern.html` | Create | Modern resume template (Jinja2) |
| `templates/resume_base.css` | Create | Shared CSS for both templates |
| `routes/resumes.py` | Modify | Add `/api/resumes/{id}/pdf` endpoint |
| `schemas.py` | Modify | Add `TemplateType` enum if needed (or just use str) |

### Frontend

| File | Change | Description |
|------|--------|-------------|
| `src/components/ResumePreview.svelte` | Modify | Add Edit/Preview mode toggle, template selector, PDF button |
| `src/components/PdfPreview.svelte` | Create | Clean PDF preview component (matches PDF output) |
| `src/components/TemplateSelector.svelte` | Create | Template selection buttons |
| `src/components/Toast.svelte` | Create | Reusable toast notification component |
| `src/lib/api.js` | Modify | Add `downloadResumePdf()` function |
| `src/styles/main.scss` | Modify | Add styles for Preview mode, template selector, toast |

### Tests

| File | Change | Description |
|------|--------|-------------|
| `tests/test_pdf_export.py` | Create | Unit tests for PDF service |
| `tests/test_pdf_api.py` | Create | Integration tests for PDF endpoint |

---

## 2. Database Changes

```sql
-- None required
-- PDF generation uses existing GeneratedResume data
-- Template preference stored in browser localStorage (Should Have)
```

---

## 3. Implementation Approach

### Service Pattern

```
PDF Generation Flow:
1. Route receives resume_id + template param
2. Route fetches GeneratedResume from resume_generator_service
3. Route calls pdf_generator_service.generate_pdf(resume, template)
4. Service loads Jinja2 template (classic/modern)
5. Service renders HTML with resume data
6. Service converts HTML to PDF via WeasyPrint
7. Route returns PDF bytes as Response

Key: pdf_generator_service is stateless, template files loaded via Jinja2 FileSystemLoader
```

### Validation

- **Route level:** Validate template is "classic" or "modern" (default "classic")
- **Route level:** Verify resume exists (404 if not)
- **Service level:** Handle WeasyPrint errors gracefully

### HTMX Patterns

N/A - This feature uses direct API call + blob download, not HTMX partials.

### Error Handling

| Error | HTTP Code | Message | Frontend Action |
|-------|-----------|---------|-----------------|
| Resume not found | 404 | "Resume not found" | Show error toast |
| Invalid template | 400 | "Invalid template. Use 'classic' or 'modern'" | Show error toast |
| PDF generation failed | 500 | "Could not generate PDF" | Show error toast with retry |

---

## 4. Implementation Order

### Phase 1: Backend Foundation

1. [ ] `requirements.txt` - Add weasyprint>=62.0, jinja2>=3.1.0
2. [ ] `templates/` - Create templates directory at project root
3. [ ] `templates/resume_base.css` - Shared CSS for PDF (page size, fonts, spacing)
4. [ ] `templates/resume_classic.html` - Classic template (serif, centered header)
5. [ ] `templates/resume_modern.html` - Modern template (sans-serif, left header)
6. [ ] `services/pdf_generator.py:PdfGeneratorService` - Core PDF generation
7. [ ] `services/pdf_generator.py:generate_pdf()` - Template load + render + WeasyPrint
8. [ ] `routes/resumes.py:export_resume_pdf()` - GET /api/resumes/{id}/pdf endpoint

### Phase 2: Backend Tests

9. [ ] `tests/test_pdf_export.py` - Test template rendering, PDF generation
10. [ ] `tests/test_pdf_api.py` - Test endpoint responses, error cases

### Phase 3: Frontend Components

11. [ ] `src/components/Toast.svelte` - Reusable toast notification
12. [ ] `src/components/TemplateSelector.svelte` - Template button group
13. [ ] `src/components/PdfPreview.svelte` - Clean PDF-matching preview
14. [ ] `src/lib/api.js:downloadResumePdf()` - Fetch PDF blob + trigger download

### Phase 4: Frontend Integration

15. [ ] `src/components/ResumePreview.svelte` - Add viewMode state (edit/preview)
16. [ ] `src/components/ResumePreview.svelte` - Add Edit/Preview toggle buttons
17. [ ] `src/components/ResumePreview.svelte` - Conditionally show editing UI vs preview
18. [ ] `src/components/ResumePreview.svelte` - Add template selector + download button
19. [ ] `src/components/ResumePreview.svelte` - Wire up PDF download with loading state
20. [ ] `src/styles/main.scss` - Preview mode styles, toast styles

### Phase 5: Polish

21. [ ] `src/components/ResumePreview.svelte` - Add success/error toasts

---

## 5. Detailed Design

### PDF Service Architecture

```python
# services/pdf_generator.py

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from pathlib import Path

class PdfGeneratorService:
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    VALID_TEMPLATES = ["classic", "modern"]

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=select_autoescape(['html'])
        )

    def generate_pdf(self, resume_data: dict, template: str = "classic") -> bytes:
        """Generate PDF from resume data using specified template."""
        if template not in self.VALID_TEMPLATES:
            raise ValueError(f"Invalid template: {template}")

        # Load template
        html_template = self.env.get_template(f"resume_{template}.html")
        css = CSS(filename=self.TEMPLATES_DIR / "resume_base.css")

        # Render HTML with resume data
        html_content = html_template.render(**self._prepare_context(resume_data))

        # Generate PDF
        html_doc = HTML(string=html_content)
        return html_doc.write_pdf(stylesheets=[css])

    def _prepare_context(self, resume_data: dict) -> dict:
        """Filter to only included sections."""
        return {
            "personal_info": resume_data.get("personal_info", {}),
            "summary": resume_data.get("summary"),
            "work_experiences": [
                exp for exp in resume_data.get("work_experiences", [])
                if exp.get("included", True)
            ],
            "skills": [
                skill for skill in resume_data.get("skills", [])
                if skill.get("included", True)
            ],
            "education": [
                edu for edu in resume_data.get("education", [])
                if edu.get("included", True)
            ],
            "projects": [
                proj for proj in resume_data.get("projects", [])
                if proj.get("included", False)  # Projects default to excluded
            ],
        }

    def generate_filename(self, resume_data: dict, company_name: str | None) -> str:
        """Generate PDF filename: FullName_Resume_Company.pdf"""
        name = resume_data.get("personal_info", {}).get("full_name", "Resume")
        company = company_name or "Company"

        # Sanitize for filename
        name = name.replace(" ", "_")
        company = company.replace(" ", "_")
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        name = "".join(c for c in name if c in safe_chars)
        company = "".join(c for c in company if c in safe_chars)

        return f"{name}_Resume_{company}.pdf"


pdf_generator_service = PdfGeneratorService()
```

### API Endpoint

```python
# routes/resumes.py (addition)

from fastapi import Query
from fastapi.responses import Response
from services.pdf_generator import pdf_generator_service

@router.get("/{resume_id}/pdf")
async def export_resume_pdf(
    resume_id: int,
    template: str = Query(default="classic", regex="^(classic|modern)$")
):
    resume = resume_generator_service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        pdf_bytes = pdf_generator_service.generate_pdf(
            resume.resume.model_dump() if resume.resume else {},
            template
        )
        filename = pdf_generator_service.generate_filename(
            resume.resume.model_dump() if resume.resume else {},
            resume.company_name
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate PDF")
```

### Template Structure

```html
<!-- templates/resume_classic.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="resume_base.css">
</head>
<body class="template-classic">
    <header>
        <h1 class="name">{{ personal_info.full_name }}</h1>
        <p class="contact">
            {{ personal_info.email }}
            {% if personal_info.phone %} | {{ personal_info.phone }}{% endif %}
        </p>
        <p class="contact">
            {% if personal_info.location %}{{ personal_info.location }}{% endif %}
            {% if personal_info.linkedin_url %} | {{ personal_info.linkedin_url }}{% endif %}
        </p>
    </header>

    {% if summary %}
    <section class="summary">
        <h2>Professional Summary</h2>
        <p>{{ summary }}</p>
    </section>
    {% endif %}

    {% if work_experiences %}
    <section class="experience">
        <h2>Experience</h2>
        {% for exp in work_experiences %}
        <div class="job">
            <div class="job-header">
                <span class="job-title">{{ exp.title }}</span>
                <span class="job-company">{{ exp.company }}</span>
                <span class="job-dates">{{ exp.start_date }} – {{ exp.end_date or 'Present' }}</span>
            </div>
            {% if exp.description %}
            <p class="job-description">{{ exp.description }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </section>
    {% endif %}

    {% if skills %}
    <section class="skills">
        <h2>Skills</h2>
        <p>{{ skills | map(attribute='name') | join(', ') }}</p>
    </section>
    {% endif %}

    {% if education %}
    <section class="education">
        <h2>Education</h2>
        {% for edu in education %}
        <p>
            {{ edu.degree }}{% if edu.field_of_study %} in {{ edu.field_of_study }}{% endif %}
            | {{ edu.institution }}
            {% if edu.graduation_year %}| {{ edu.graduation_year }}{% endif %}
        </p>
        {% endfor %}
    </section>
    {% endif %}

    {% if projects %}
    <section class="projects">
        <h2>Projects</h2>
        {% for project in projects %}
        <div class="project">
            <p class="project-name">{{ project.name }}</p>
            {% if project.description %}<p>{{ project.description }}</p>{% endif %}
            {% if project.technologies %}<p class="technologies">{{ project.technologies }}</p>{% endif %}
        </div>
        {% endfor %}
    </section>
    {% endif %}
</body>
</html>
```

### Frontend State Management

```svelte
<!-- ResumePreview.svelte (additions) -->
<script>
  // New state
  let viewMode = $state('edit'); // 'edit' or 'preview'
  let selectedTemplate = $state('classic');
  let isExporting = $state(false);
  let toastMessage = $state(null);
  let toastType = $state('success');

  // PDF download
  async function downloadPdf() {
    isExporting = true;
    try {
      const response = await fetch(
        `/api/resumes/${resume.id}/pdf?template=${selectedTemplate}`
      );
      if (!response.ok) throw new Error('Failed to generate PDF');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Extract filename from Content-Disposition header
      const disposition = response.headers.get('Content-Disposition');
      const match = disposition?.match(/filename="(.+)"/);
      a.download = match?.[1] || 'resume.pdf';

      a.click();
      URL.revokeObjectURL(url);

      showToast('PDF downloaded', 'success');
    } catch (e) {
      showToast('Could not generate PDF. Please try again.', 'error');
    } finally {
      isExporting = false;
    }
  }

  function showToast(message, type = 'success') {
    toastMessage = message;
    toastType = type;
    setTimeout(() => toastMessage = null, 3000);
  }
</script>
```

---

## 6. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| WeasyPrint system deps missing | Med | High | Verify in dev setup, tests will fail clearly |
| PDF preview != actual PDF | Low | Med | Use same HTML/CSS for browser preview |
| Large resumes slow to generate | Low | Low | PDF gen is ~1-2s, acceptable for MVP |
| Template CSS differs in WeasyPrint | Med | Med | Test both templates with WeasyPrint early |

---

## 7. File Structure After Implementation

```
MyCV-2/
├── requirements.txt          # Modified: +weasyprint, +jinja2
├── templates/                 # NEW directory
│   ├── resume_base.css       # Shared PDF styles
│   ├── resume_classic.html   # Classic template
│   └── resume_modern.html    # Modern template
├── services/
│   └── pdf_generator.py      # NEW: PDF generation service
├── routes/
│   └── resumes.py            # Modified: +pdf endpoint
├── src/
│   ├── components/
│   │   ├── ResumePreview.svelte  # Modified: +modes, +template, +download
│   │   ├── PdfPreview.svelte     # NEW: Clean preview
│   │   ├── TemplateSelector.svelte # NEW: Template buttons
│   │   └── Toast.svelte          # NEW: Notifications
│   ├── lib/
│   │   └── api.js            # Modified: +downloadResumePdf
│   └── styles/
│       └── main.scss         # Modified: +preview styles
└── tests/
    ├── test_pdf_export.py    # NEW: PDF service tests
    └── test_pdf_api.py       # NEW: API tests
```

---

*Next: /v3-checklist*
