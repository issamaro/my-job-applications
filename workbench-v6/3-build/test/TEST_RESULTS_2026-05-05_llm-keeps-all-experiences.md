feature: llm-keeps-all-experiences
date: 2026-05-05
status: PARTIAL

## Test Results

### Targeted Tests (Feature-specific)
Command: `uv run python -m pytest tests/test_resume_prompts.py tests/test_resume_generator.py tests/test_resumes.py tests/test_chronological_order.py -v`
Exit Code: 0
Result: 41 passed, 0 failed
Duration: 0.78s

### Full Test Suite
Command: `uv run python -m pytest -v`
Exit Code: 1
Result: 205 passed, 16 failed
Duration: 6.36s

## Failures

All 16 failures are in PDF-related tests and stem from a single root cause: Playwright browser executable not installed.

### Failed Tests (root cause: Playwright chromium executable missing)

1. **test_export_pdf_returns_pdf** @ tests/test_pdf_api.py:80
   Error: BrowserType.launch: Executable doesn't exist at .venv/lib/python3.13/site-packages/playwright/driver/package/.local-browsers/chromium_headless_shell-1208/chrome-headless-shell-mac-arm64/chrome-headless-shell
   Traceback: Playwright error suggesting `playwright install` needed

2. **test_export_pdf_default_template_is_classic** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

3. **test_export_pdf_with_modern_template** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

4. **test_export_pdf_content_disposition_header** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

5. **test_export_pdf_filename_format** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

6. **test_export_pdf_with_classic_template_param** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

7. **test_export_pdf_brussels_template** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

8. **test_export_pdf_eu_classic_template** @ tests/test_pdf_api.py
   Error: Same BrowserType.launch error

9. **test_generate_pdf_classic_template** @ tests/test_pdf_export.py
   Error: Same BrowserType.launch error

10. **test_generate_pdf_modern_template** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

11. **test_empty_sections_handling** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

12. **test_generate_pdf_brussels_template** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

13. **test_generate_pdf_eu_classic_template** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

14. **test_generate_pdf_with_photo** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

15. **test_generate_pdf_without_photo_shows_placeholder** @ tests/test_pdf_export.py
    Error: Same BrowserType.launch error

16. **test_generate_pdf_accepts_language_parameter** @ tests/test_pdf_language.py
    Error: Same BrowserType.launch error

## Key Findings

- **Feature Tests Pass**: All 41 directly affected tests for `llm-keeps-all-experiences` pass completely (test_resume_prompts.py, test_resume_generator.py, test_resumes.py, test_chronological_order.py).
- **Regression Analysis**: No regressions introduced by the feature. The 16 failures are pre-existing environmental issues with Playwright, not caused by the feature changes.
- **Root Cause**: Playwright browser drivers are missing from the environment. This is an infrastructure issue, not a code defect. Error message indicates: `playwright install` is needed.

## Decisions

none — caller triages failures
