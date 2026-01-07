# Test Results: add-language

**Date:** 2026-01-07
**Feature:** Add Language Management

## Dependency Verification

```
pytest v9.0.2 (required: >=8.0.0) ✓
fastapi v0.128.0 (required: >=0.100.0) ✓
```

## Unit Tests

**Command:** `uv run pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration`

**Result:** 131 passed, 1 failed

| Metric | Value |
|--------|-------|
| Total Tests | 132 |
| Passed | 131 |
| Failed | 1 |
| Duration | 11.56s |

### Language Tests (Feature-Specific)

All 11 language tests passed:
- `test_list_languages_empty` ✓
- `test_add_language` ✓
- `test_add_language_invalid_level` ✓
- `test_edit_language` ✓
- `test_delete_language` ✓
- `test_reorder_languages` ✓
- `test_get_nonexistent_language` ✓
- `test_delete_nonexistent_language` ✓
- `test_all_cefr_levels_accepted` ✓
- `test_add_language_empty_name` ✓
- `test_languages_in_profile_complete` ✓

## Integration Tests

**Command:** `uv run pytest tests/integration/ -v`

**Result:** N/A - No integration test directory exists

## E2E Tests

**Command:** `uv run pytest tests/e2e/ -v`

**Result:** N/A - No E2E test directory exists

## Coverage

**Command:** `uv run pytest --cov=. --cov-report=term`

**Result:** N/A - pytest-cov not installed in dev dependencies

## Known Issues

| Test | Status | Reason |
|------|--------|--------|
| `test_data_url_too_large` | SKIPPED | Unrelated to add-language feature; photos endpoint validation issue |

### Failure Details

```
tests/test_photos.py::test_data_url_too_large FAILED
- Expected: 422 (validation error for oversized data URL)
- Actual: 200 (request accepted)
- Cause: Missing validation for 500k+ character data URLs in photos endpoint
```

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Test failure triage (1 failed) | D) Skip for now | Documented as known issue; unrelated to add-language feature |

## Status

| Status | Reason |
|--------|--------|
| **PASS** | All add-language feature tests pass; 1 unrelated failure documented |

## Next Step

→ /v5-inspect
