# Test Dependency Fix

Source: PHOTO-MANAGEMENT retrospective
Date: 2026-01-04

Pytest test suite fails due to starlette/httpx version incompatibility.

## Error

```
TypeError: Client.__init__() got an unexpected keyword argument 'app'
```

All tests using TestClient fail at setup, not during test execution.

## Why It Matters

- Cannot run automated tests reliably
- Blocks CI/CD pipeline (if implemented)
- Manual API testing is slow and error-prone

## Root Cause

The TestClient from starlette uses httpx under the hood. Recent httpx versions changed the Client API, breaking TestClient instantiation.

## Potential Fixes

1. **Pin dependency versions** - Lock httpx to compatible version
2. **Upgrade starlette** - May have fixed TestClient for newer httpx
3. **Use httpx directly** - Replace TestClient with httpx.AsyncClient
4. **Switch to requests** - More stable, sync-only but sufficient for tests

## Priority

High - Automated tests are essential for confidence in changes.
