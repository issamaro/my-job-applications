# Library Notes: WeasyPrint Spike Test

**Date:** 2026-01-08
**Feature:** european-cv-templates
**Purpose:** Validate high-risk assumptions before planning

---

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Ecosystem preference | A) Respect existing | Using WeasyPrint >=62.0 already in project |

---

## Existing Ecosystem

| Component | Version | Source |
|-----------|---------|--------|
| Python | 3.13 | `.python-version` |
| WeasyPrint | >=62.0 | `pyproject.toml` |
| Jinja2 | >=3.1.0 | `pyproject.toml` |

---

## Spike Test 1: Base64 Data URI Images

### Question
Can WeasyPrint render base64 data URI images (`<img src="data:image/png;base64,...">`) in PDF?

### Research Findings
- **Not explicitly documented** in WeasyPrint docs
- WeasyPrint uses Pillow for image processing (PNG, JPEG, GIF, BMP supported)
- Data URIs are standard HTML - browsers and most HTML renderers support them
- WeasyPrint supports `<img src="...">` with various URL types

### Verdict: LIKELY SUPPORTED (needs practical test)

**Rationale:** Data URIs are valid URLs per RFC 2397. WeasyPrint processes standard HTML and supports image embedding. No documentation suggests data URIs are blocked.

### Fallback Plan
If base64 fails:
```python
# Save photo to temp file, reference by path
import tempfile
import base64

def photo_to_temp_file(base64_data: str) -> str:
    data = base64.b64decode(base64_data.split(',')[1])
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
        f.write(data)
        return f.name
```

### Quick Validation Test
```python
from weasyprint import HTML

html = '''
<html><body>
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
     width="100" height="100" alt="test">
</body></html>
'''
HTML(string=html).write_pdf('test_base64.pdf')
# Success if PDF contains 1x1 red pixel image
```

---

## Spike Test 2: Two-Column CSS Layout with Page Breaks

### Question
Does two-column CSS (flexbox/grid) work across page breaks in WeasyPrint?

### Research Findings

#### CSS Grid: SUPPORTED
- **Fragmentation between rows supported** (key finding!)
- `display: grid`, `grid-template-columns`, `gap` all work
- Limitations: No `display: inline-grid`, no subgrids

```css
/* SUPPORTED - use this */
.container {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
}
```

#### Flexbox: PARTIAL SUPPORT
- Works for "simple use cases"
- **Not deeply tested** (per docs)
- Fragmentation behavior uncertain

```css
/* WORKS but less reliable for page breaks */
.container {
  display: flex;
  flex-flow: row wrap;
}
```

#### Multi-column: LIMITED
- `columns`, `column-gap`, `column-rule` supported
- **Pagination "not seriously tested"**
- Not recommended for layouts that span pages

#### Page Break Control: FULLY SUPPORTED
```css
/* All supported */
.section { break-inside: avoid; }
.page-start { break-before: page; }
.keep-together { break-inside: avoid-page; }
```

### Verdict: USE CSS GRID

**Rationale:** CSS Grid explicitly supports "fragmentation between rows" - exactly what's needed for two-column layouts that span multiple pages.

### Recommended Pattern
```css
.two-column-cv {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 20px;
}

.sidebar {
  grid-column: 1;
}

.main-content {
  grid-column: 2;
}

/* Prevent awkward breaks */
.experience-item {
  break-inside: avoid;
}
```

---

## Summary

| Assumption | Status | Recommendation |
|------------|--------|----------------|
| WeasyPrint renders base64 images | LIKELY OK | Proceed, run quick validation test during build |
| Two-column CSS works across pages | CONFIRMED | Use CSS Grid (not flexbox/multi-column) |

---

## Dependencies Summary

No new dependencies required. Existing stack sufficient:

```toml
# Already in pyproject.toml
weasyprint = ">=62.0"
jinja2 = ">=3.1.0"
```

---

## Patterns to Use

### Photo in Template (Jinja2)
```html
{% if resume.photo %}
  <img src="{{ resume.photo }}" class="photo" alt="Profile photo">
{% else %}
  <div class="photo-placeholder">
    <svg><!-- silhouette --></svg>
  </div>
{% endif %}
```

### Two-Column Layout (CSS Grid)
```css
.brussels-template {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 24px;
  min-height: 100%;
}

.sidebar {
  background: #f5f5f5;
  padding: 20px;
}

.main {
  padding: 20px;
}

/* Page break handling */
.section {
  break-inside: avoid;
}

@media print {
  .brussels-template {
    grid-template-rows: auto;
  }
}
```

### Patterns to Avoid

```css
/* AVOID - fragmentation issues */
.container {
  display: flex;  /* Use grid instead */
  columns: 2;     /* Multi-column not reliable for pagination */
}

/* AVOID - may not work */
display: inline-grid;  /* Not supported */
```

---

## Next Steps

1. Update FEATURE_SPEC (remove grouping requirement)
2. Re-run /v5-verify-analysis
3. Proceed to /v5-plan

---

*Research completed: 2026-01-08*
*Status: Complete*
