# Fix Photo Validation Test

Source: project-tooling-standardization retrospective
Date: 2026-01-06

---

## Issue

Test `test_data_url_too_large` in `tests/test_photos.py:122` is failing:

```python
assert response.status_code == 422  # Expected
# Actual: 200
```

The test expects the API to reject a data URL that exceeds size limits, but the API is accepting it.

## Root Cause

Either:
1. The validation for photo data URL size is missing/broken
2. The test expectation is wrong

## Potential Approaches

- Review the photo upload validation logic
- Check if there's a size limit configured
- Determine if this is a test bug or application bug
- Fix whichever is incorrect
