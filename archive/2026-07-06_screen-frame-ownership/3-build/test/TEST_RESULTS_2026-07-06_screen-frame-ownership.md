---
feature: screen-frame-ownership
date: 2026-07-06
status: PASS
---

## Test Results

| Level | Command | Exit | Counts | Duration |
|-------|---------|------|--------|----------|
| unit | `uv run pytest tests/ -v` | 0 | 286 passed, 0 failed | 32.81s |

## Coverage

n/a (pytest-cov not configured)

## Failures

None.

## Notes

- No Playwright test skips detected; bundle.css verified as current
- Changed/new tests verified:
  - tests/test_generator_frame.py (new): 1 test passed
  - tests/test_design_tokens.py (extended): 4 tests passed
  - tests/test_topbar_shell.py (retargeted): 11 tests passed
- Node test suite skipped (npm not available in environment)

## Decisions

none — caller triages failures
