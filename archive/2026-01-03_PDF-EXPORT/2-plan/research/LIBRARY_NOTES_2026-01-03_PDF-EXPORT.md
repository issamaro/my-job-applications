# Library Notes: PDF Export

**Date:** 2026-01-03
**Purpose:** Ecosystem prerequisites and syntax reference for implementation

---

## 0. Ecosystem Prerequisites

### Runtime (from context7 lookups)

| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Already pinned in project; WeasyPrint requires 3.9+, all libs compatible |
| Node | 20 | Already pinned in project; Svelte 5 compatible |

### Tooling

| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python version + venv + packages | `uv --version` |
| nvm | Node version management | `nvm --version` |
| npm | Node packages | `npm --version` |

### Setup Commands

```bash
# Python (already configured)
source .venv/bin/activate
uv pip install -r requirements.txt

# Node (already configured)
nvm use
npm install
```

---

## WeasyPrint (NEW)

**Version Constraint:** `weasyprint>=62.0`

WeasyPrint is a visual rendering engine for HTML and CSS that exports to PDF. Version 62.0 added CSS Grid and nesting support.

### System Dependencies

WeasyPrint requires system libraries. On macOS:
```bash
brew install pango libffi
```

### Correct Patterns

- `HTML(string='...')` - Create HTML from string (must use named parameter)
- `CSS(string='...')` - Create CSS from string (must use named parameter)
- `html.write_pdf(target, stylesheets=[css])` - Generate PDF with stylesheets
- `FontConfiguration()` - Configure custom fonts

### Code Examples

```python
from weasyprint import HTML, CSS

# Basic HTML to PDF
html = HTML(string='''
    <h1>Resume</h1>
    <p>Content here</p>
''')
css = CSS(string='''
    @page { size: letter; margin: 1in; }
    body { font-family: Arial, sans-serif; }
''')

# Write to bytes (for API response)
pdf_bytes = html.write_pdf(stylesheets=[css])

# Write to file
html.write_pdf('/tmp/resume.pdf', stylesheets=[css])
```

### Page Size Configuration

```python
# US Letter size (standard for resumes)
CSS(string='@page { size: letter; margin: 0.75in; }')

# A4 size (international)
CSS(string='@page { size: A4; margin: 2cm; }')
```

### ATS-Friendly Fonts

```css
/* Use system fonts for maximum ATS compatibility */
body {
    font-family: Arial, Helvetica, sans-serif;
}
h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
}
```

---

## Jinja2 (NEW)

**Version Constraint:** `jinja2>=3.1.0`

Jinja2 is used for HTML template rendering. Templates define resume layouts.

### Correct Patterns

- `Environment(loader=..., autoescape=True)` - Create env with autoescaping
- `env.get_template('name.html')` - Load template from file
- `env.from_string(source)` - Load template from string
- `template.render(**context)` - Render with variables

### Code Examples

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup environment with templates directory
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Load and render template
template = env.get_template('resume_classic.html')
html_output = template.render(
    personal_info=resume.personal_info,
    summary=resume.summary,
    work_experiences=resume.work_experiences,
    skills=resume.skills,
    education=resume.education,
    projects=resume.projects
)
```

### Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <header>
        <h1>{{ personal_info.full_name }}</h1>
        <p>{{ personal_info.email }} | {{ personal_info.phone }}</p>
    </header>

    {% if summary %}
    <section class="summary">
        <h2>Summary</h2>
        <p>{{ summary }}</p>
    </section>
    {% endif %}

    {% for exp in work_experiences if exp.included %}
    <section class="experience">
        <h3>{{ exp.title }} at {{ exp.company }}</h3>
        <p>{{ exp.description }}</p>
    </section>
    {% endfor %}
</body>
</html>
```

---

## FastAPI (existing)

**Version Constraint:** `fastapi>=0.100.0` (already in requirements.txt)

### Correct Patterns for File Download

- `FileResponse(path, filename=..., media_type=...)` - Return file from disk
- `Response(content, media_type=..., headers=...)` - Return bytes directly
- `StreamingResponse(generator, media_type=...)` - Stream large files

### Code Examples

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

@app.get("/api/resumes/{resume_id}/pdf")
async def export_resume_pdf(
    resume_id: int,
    template: str = "classic"
):
    # Generate PDF bytes
    pdf_bytes = generate_pdf(resume_id, template)

    # Return as downloadable file
    filename = f"John_Doe_Resume_Acme.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
```

### Content-Disposition Header

```python
# For download (prompts save dialog)
headers={"Content-Disposition": 'attachment; filename="resume.pdf"'}

# For inline viewing (opens in browser)
headers={"Content-Disposition": 'inline; filename="resume.pdf"'}
```

---

## Pydantic (existing)

**Version Constraint:** `pydantic>=2.0` (already in requirements.txt)

### Correct Patterns (v2)

- `model_config = ConfigDict(from_attributes=True)` - Enable ORM mode
- `.model_validate(obj)` - Create model from dict/ORM object
- `.model_dump()` - Convert model to dict
- `.model_dump(exclude_none=True)` - Exclude None values

### Deprecated (Avoid)

| Old (v1) | New (v2) |
|----------|----------|
| `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `.from_orm(obj)` | `.model_validate(obj)` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |

### Code Examples

```python
from pydantic import BaseModel, ConfigDict

class ResumeExportRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: int
    template: str = "classic"

# From ORM object
resume_model = ResumeModel.model_validate(db_resume)

# To dict for template rendering
context = resume_model.model_dump()
```

---

## Svelte 5 (existing)

**Version Constraint:** `svelte>=5.0.0` (already in package.json as ^5.0.0)

### Correct Patterns (Svelte 5 Runes)

- `let count = $state(0)` - Reactive state (replaces `let count = 0`)
- `let doubled = $derived(count * 2)` - Computed values (replaces `$: doubled = count * 2`)
- `onclick={() => ...}` - Event handlers (replaces `on:click`)

### Deprecated (Avoid in Svelte 5)

| Old (Svelte 4) | New (Svelte 5) |
|----------------|----------------|
| `let x = 0` (reactive) | `let x = $state(0)` |
| `$: doubled = x * 2` | `let doubled = $derived(x * 2)` |
| `on:click={handler}` | `onclick={handler}` |
| `export let prop` | `let { prop } = $props()` |

### Code Examples

```svelte
<script>
    let isExporting = $state(false);
    let selectedTemplate = $state('classic');

    async function downloadPdf() {
        isExporting = true;
        try {
            const response = await fetch(`/api/resumes/${resumeId}/pdf?template=${selectedTemplate}`);
            const blob = await response.blob();

            // Trigger download
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${name}_Resume_${company}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
        } finally {
            isExporting = false;
        }
    }
</script>

<button onclick={downloadPdf} disabled={isExporting}>
    {isExporting ? 'Generating...' : 'Download PDF'}
</button>
```

### Template Selector Pattern

```svelte
<script>
    let selectedTemplate = $state('classic');
    const templates = [
        { id: 'classic', name: 'Classic', description: 'Traditional serif fonts' },
        { id: 'modern', name: 'Modern', description: 'Clean sans-serif design' }
    ];
</script>

<div class="template-selector">
    {#each templates as template}
        <button
            class:selected={selectedTemplate === template.id}
            onclick={() => selectedTemplate = template.id}
        >
            {template.name}
        </button>
    {/each}
</div>
```

---

## Dependencies Summary

**ADD TO requirements.txt:**

```
weasyprint>=62.0
jinja2>=3.1.0
```

**EXISTING (no changes needed):**

```
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
```

**EXISTING package.json (no changes needed):**

```json
"svelte": "^5.0.0"
```

---

## System Dependencies Note

WeasyPrint requires system libraries for PDF rendering:

**macOS:**
```bash
brew install pango libffi
```

**Ubuntu/Debian:**
```bash
apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

This should be documented in the project README for developer setup.

---

*Reference for /v3-design and /v3-checklist*
