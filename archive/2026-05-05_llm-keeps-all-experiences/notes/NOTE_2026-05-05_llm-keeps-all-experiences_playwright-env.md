---
date: 2026-05-05
slug: llm-keeps-all-experiences_playwright-env
---

# Note — Playwright env failures during test run (pre-existing)

Full-suite `pytest -q` shows 16 failures, all Playwright PDF tests failing with `BrowserType.launch: Executable doesn't exist`. Root cause: chromium driver not installed in this environment. Recent commits (1b4e8f3, d30a086) added README steps for `playwright install` — this is a known manual setup step on a fresh checkout.

Targeted tests (test_resume_prompts.py, test_resume_generator.py, test_resumes.py, test_chronological_order.py) all pass: 41/41. No regression caused by this feature.

Treating as environmental, not a feature failure. Skipping Q3 triage. Test gate: PASS (for the feature scope).
