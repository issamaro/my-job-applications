# Note: WeasyPrint Missing System Dependencies

**Date:** 2026-01-04
**Category:** ENVIRONMENT
**During:** /v4-test

---

## What Happened

10 PDF-related tests fail because WeasyPrint cannot load required system libraries.

## Context

- **File(s):** `tests/test_pdf_api.py`, `tests/test_pdf_export.py`, `services/pdf_generator.py`
- **Expected:** PDF tests should pass
- **Actual:** `OSError: cannot load library 'libgobject-2.0-0'`

---

## Error Details

```
OSError: cannot load library 'libgobject-2.0-0': dlopen(libgobject-2.0-0, 0x0002):
tried: 'libgobject-2.0-0' (no such file), '/usr/lib/libgobject-2.0-0' (no such file, not in dyld cache)
```

WeasyPrint requires system libraries (GTK/Pango/GObject) that are not installed via pip - they must be installed at the OS level.

---

## Resolution

**Not resolved** - This is an environment setup issue, not a code issue.

### To Fix (macOS)

```bash
brew install pango gdk-pixbuf libffi
```

### To Fix (Linux)

```bash
apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

---

## Impact

- **Immediate:** 10 tests fail, but they are unrelated to Photo Management feature. Feature tests (102/102 non-PDF) all pass.
- **Future:** Yes - should add to backlog: "Install WeasyPrint system dependencies"
- **Checklist:** Yes - add to PROJECT_CHECKS.md or dev setup docs

---

## Affected Tests

| Test | File |
|------|------|
| test_export_pdf_returns_pdf | test_pdf_api.py |
| test_export_pdf_default_template_is_classic | test_pdf_api.py |
| test_export_pdf_with_modern_template | test_pdf_api.py |
| test_export_pdf_content_disposition_header | test_pdf_api.py |
| test_export_pdf_filename_format | test_pdf_api.py |
| test_export_pdf_with_classic_template_param | test_pdf_api.py |
| test_generate_pdf_classic_template | test_pdf_export.py |
| test_generate_pdf_modern_template | test_pdf_export.py |
| test_generate_pdf_invalid_template | test_pdf_export.py |
| test_empty_sections_handling | test_pdf_export.py |

---

## Recommendation

Add to project setup documentation:

```markdown
## PDF Export Requirements

WeasyPrint requires system libraries for PDF generation:

### macOS
brew install pango gdk-pixbuf libffi

### Linux (Debian/Ubuntu)
apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

---

*Captured during PHOTO-MANAGEMENT /v4-test*
