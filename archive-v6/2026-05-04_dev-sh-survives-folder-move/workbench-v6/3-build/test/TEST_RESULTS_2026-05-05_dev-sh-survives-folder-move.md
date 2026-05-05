---
feature: dev-sh-survives-folder-move
date: 2026-05-05
status: PASS
---

## Test Execution Results

| Level | Command | Exit Code | Result | Duration |
|-------|---------|-----------|--------|----------|
| Unit | `uv run pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration` | 0 | 218 passed, 0 failed | 8.79s |
| Integration | Skipped (folder does not exist) | - | - | - |
| E2E | Skipped (excluded from pytest collection) | - | - | - |
| Coverage | Skipped (per request) | - | - | - |

## Summary

All 218 unit tests pass. No failures detected. The 1-token swap in `dev.sh` (`uv run uvicorn` → `uv run python -m uvicorn`) plus README/PROJECT_CHECKS.md doc edits introduce no regressions in the test suite.

## Decisions

none — caller triages failures
