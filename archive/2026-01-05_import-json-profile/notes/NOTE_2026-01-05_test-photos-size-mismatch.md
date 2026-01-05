# Note: test_photos.py Size Validation Test Out of Sync

**Date:** 2026-01-05
**Category:** QUIRK
**During:** /v4-test

---

## What Happened

Running all tests revealed a failing test `test_data_url_too_large` in `tests/test_photos.py`. The test was written for an earlier schema validation limit but the schema was later updated (bug fix) without updating the corresponding test.

## Context

- **File(s):** `tests/test_photos.py:122`, `schemas.py:327-334`
- **Expected:** Test and schema should have matching size limits
- **Actual:** Test expects 422 for ~500KB images, but `PhotoUpload` schema allows up to 15MB

### Test Code (test_photos.py:114-122)
```python
def test_data_url_too_large(client):
    """PUT with oversized data returns 422."""
    create_personal_info(client)

    # Create a data URL larger than 500,000 characters
    large_base64 = base64.b64encode(b"x" * 400000).decode()
    large_data_url = f"data:image/jpeg;base64,{large_base64}"

    response = client.put("/api/photos", json={"image_data": large_data_url})
    assert response.status_code == 422  # Fails - returns 200
```

### Schema Code (schemas.py:327-334)
```python
@field_validator("image_data")
@classmethod
def validate_image_data(cls, v: str) -> str:
    if not re.match(r"^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$", v):
        raise ValueError("Invalid image data format")
    # 10MB file becomes ~13.3MB as base64, allow 15MB for safety
    if len(v) > 15_000_000:  # Test expects ~500KB limit
        raise ValueError("Image data too large")
    return v
```

---

## Resolution

Not fixed during Import JSON Profile implementation as it's unrelated to the feature. Documented for future fix.

**Fix required:** Update `test_data_url_too_large` to use a file larger than 15MB, or add a new test that validates the actual 15MB limit.

---

## Impact

- **Immediate:** None - unrelated to Import JSON Profile feature
- **Future:** Yes - add to backlog to fix test
- **Checklist:** No - this is a one-time test fix, not a recurring pattern

---

*Captured during Import JSON Profile implementation*
