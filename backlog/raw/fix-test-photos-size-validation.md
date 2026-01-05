# Fix test_photos.py Size Validation Test

Source: import-json-profile retrospective
Date: 2026-01-05

The `test_data_url_too_large` test in `tests/test_photos.py` is out of sync with the `PhotoUpload` schema. The test expects 422 for ~500KB images but the schema was updated to allow up to 15MB.

This was discovered when running all tests - the test fails because the schema was fixed but the test wasn't updated.

Potential approaches:
- Update test to use a file larger than 15MB to trigger the validation error
- Add a new test that validates the actual 15MB limit
- Consider if 15MB is the correct limit or if it should be lower
