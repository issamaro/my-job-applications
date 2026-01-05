# Note: WeasyPrint macOS SIP Subprocess Workaround

**Date:** 2026-01-05
**Category:** WORKAROUND
**During:** Bug fix (PDF generation broken)

---

## What Happened

WeasyPrint PDF generation stopped working. The library requires native C libraries (glib, pango, cairo) which need `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` to be found on macOS with Homebrew.

Despite setting this variable:
- In `.zshrc`
- At the top of `dev.sh`
- Inline with the uvicorn command

The variable was being stripped and WeasyPrint couldn't load its dependencies.

## Context

- **File(s):** `services/pdf_generator.py`, `dev.sh`
- **Expected:** `DYLD_FALLBACK_LIBRARY_PATH` would be inherited by uvicorn process
- **Actual:** macOS SIP (System Integrity Protection) strips `DYLD_*` variables from child processes in certain contexts

---

## Root Cause Analysis

| Test | Result |
|------|--------|
| Direct Python with DYLD set | Works |
| uvicorn with DYLD in environment | Fails |
| uvicorn --reload subprocess | Fails |
| uvicorn without --reload | Fails |
| VS Code terminal | Fails |
| Fresh terminal window | Fails |

macOS SIP aggressively strips `DYLD_*` environment variables from child processes for security reasons. This affects:
- Processes spawned by other processes
- Scripts run in certain terminal contexts
- Subprocess chains (parent → child)

---

## Resolution

**Solution:** Run WeasyPrint in an isolated subprocess where we explicitly set the environment variable at spawn time.

### New File: `services/pdf_subprocess.py`

```python
#!/usr/bin/env python3
"""Isolated subprocess for PDF generation with DYLD set."""
import sys
from pathlib import Path

def generate_pdf(html_path: str, css_path: str, output_path: str) -> None:
    from weasyprint import HTML, CSS
    html_doc = HTML(filename=html_path)
    css = CSS(filename=css_path)
    html_doc.write_pdf(output_path, stylesheets=[css])

if __name__ == "__main__":
    html_path, css_path, output_path = sys.argv[1:4]
    generate_pdf(html_path, css_path, output_path)
```

### Updated: `services/pdf_generator.py`

```python
def generate_pdf(self, resume_data: dict, template: str = "classic") -> bytes:
    # Render HTML to temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "resume.html"
        pdf_path = Path(tmpdir) / "resume.pdf"
        html_path.write_text(html_content)

        # Spawn subprocess with explicit DYLD
        env = os.environ.copy()
        env["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"

        result = subprocess.run(
            [sys.executable, str(self.SUBPROCESS_SCRIPT),
             str(html_path), str(css_path), str(pdf_path)],
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"PDF generation failed: {result.stderr}")

        return pdf_path.read_bytes()
```

---

## Why This Works

1. `subprocess.run()` with explicit `env=` parameter sets the environment for the new process at the OS level
2. The subprocess is a fresh Python interpreter, not a child of uvicorn's process chain
3. DYLD is set before the Python interpreter starts, so cffi/WeasyPrint can load native libraries

---

## Impact

- **Immediate:** PDF generation works regardless of how the server is started
- **Future:** No - this is a permanent architectural solution
- **Checklist:** Yes - document for future macOS developers

---

## Checklist Item

Add to PROJECT_CHECKS.md:

```markdown
### PDF Generation (macOS)

- [ ] WeasyPrint uses subprocess pattern (`services/pdf_subprocess.py`)
- [ ] Never import WeasyPrint directly in uvicorn process
- [ ] Homebrew libs installed: `brew install pango gdk-pixbuf glib cairo`
```

---

## Key Learnings

1. **macOS SIP is aggressive** - DYLD_* variables are stripped in many contexts, not just for system binaries
2. **Subprocess isolation works** - Setting env at subprocess.run() time bypasses SIP restrictions
3. **Direct Python test ≠ Server test** - Always test in the actual runtime context (uvicorn)
4. **Package location matters** - Ensure packages are in venv, not system Python (use `uv pip install`)

---

*Captured during PDF generation bug fix*
