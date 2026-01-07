# Implementation Checklist: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language

## 0. Ecosystem Verification

| Component | Version | Verify Command | Target |
|-----------|---------|----------------|--------|
| Python | 3.13 | `python --version` | `.python-version` |
| Node | 20 | `node --version` | `.nvmrc` |
| Virtual env | Active | `which python` should show `.venv` | `.venv/` |

**Checklist:**
- [ ] Python 3.13 installed and active
- [ ] Node 20.x installed
- [ ] Virtual environment activated (`source .venv/bin/activate`)

**STOP if ecosystem not ready.**

## 1. Dependency Verification

| Library | Constraint | Manifest | Status |
|---------|------------|----------|--------|
| FastAPI | >=0.100.0 | `pyproject.toml` | Existing |
| Pydantic | >=2.0 | `pyproject.toml` | Existing |
| Svelte | ^5.0.0 | `package.json` | Existing |

**Checklist:**
- [ ] No new dependencies required - all existing
- [ ] `uv sync` runs without errors
- [ ] `npm install` runs without errors

**STOP if any dependency missing.**

## 2. Syntax Verification

### Pydantic 2 Patterns
- [ ] `CEFRLevel(str, Enum)` uses str inheritance for JSON serialization → `schemas.py`
- [ ] `@field_validator` decorator (not `@validator`) → `schemas.py`
- [ ] `model_validate(dict(row))` for SQLite Row conversion → `routes/languages.py`
- [ ] `ConfigDict(from_attributes=True)` on response models → `schemas.py`

### FastAPI Patterns
- [ ] `APIRouter(prefix="/api/languages", tags=["languages"])` → `routes/languages.py`
- [ ] `response_model=list[Language]` on GET endpoint → `routes/languages.py`
- [ ] `HTTPException(status_code=404)` for not found → `routes/languages.py`
- [ ] Path parameter `lang_id: int` type annotation → `routes/languages.py`

### Svelte 5 Patterns
- [ ] `$state([])` for reactive arrays → `Languages.svelte`
- [ ] `$effect()` for mount-time data fetch → `Languages.svelte`
- [ ] `onclick` property (not `on:click`) → `Languages.svelte`
- [ ] `ondragstart`, `ondragover`, `ondrop` properties → `Languages.svelte`
- [ ] `bind:value` for form inputs → `Languages.svelte`
- [ ] `export function add()` for parent-triggered actions → `Languages.svelte`

### SQLite Patterns
- [ ] `CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2'))` constraint → `database.py`
- [ ] `INTEGER NOT NULL DEFAULT 0` for display_order → `database.py`
- [ ] `DEFAULT CURRENT_TIMESTAMP` for created_at/updated_at → `database.py`

## 3. UX Verification

### Empty State
- [ ] "No languages added yet." displayed when list empty → `Languages.svelte`
- [ ] Section remains visible with "+" button enabled → `Languages.svelte`

### Loading State
- [ ] Skeleton placeholder shown during fetch → `Languages.svelte`
- [ ] Loading state prevents form interactions → `Languages.svelte`

### Success States
- [ ] "Saved" indicator appears after save, fades after 2s → `Languages.svelte`
- [ ] Form closes after successful save → `Languages.svelte`
- [ ] List updates immediately after add/edit/delete → `Languages.svelte`

### Error States
- [ ] "Could not load profile. Please refresh." on load failure → `Languages.svelte`
- [ ] "Could not save. Please try again." on save failure → `Languages.svelte`
- [ ] "Could not delete. Please try again." on delete failure → `Languages.svelte`
- [ ] "Required" inline error for empty name field → `Languages.svelte`
- [ ] "Required" inline error for unselected level → `Languages.svelte`

### Form UX
- [ ] Name input is text field with required indicator (*) → `Languages.svelte`
- [ ] Level is `<select>` dropdown with CEFR options → `Languages.svelte`
- [ ] Dropdown options show descriptions: "A1 (Beginner)" etc. → `Languages.svelte`
- [ ] Save/Cancel buttons in form actions → `Languages.svelte`
- [ ] Delete link shown only in edit mode → `Languages.svelte`

### Drag-and-Drop UX
- [ ] Drag handle (⋮⋮) visible on each item → `Languages.svelte`
- [ ] Visual feedback during drag (cursor change) → `Languages.svelte`
- [ ] Order persists to database after drop → `Languages.svelte`

### Delete Confirmation
- [ ] ConfirmDialog appears on delete click → `Languages.svelte`
- [ ] Message: "Delete this language?" → `Languages.svelte`
- [ ] Confirm/Cancel buttons in dialog → `Languages.svelte`

### Resume Preview
- [ ] Languages section with toggle control → `ResumePreview.svelte`
- [ ] Format: "French - B2" (code only, no description) → `ResumePreview.svelte`
- [ ] Toggle off shows "(Section hidden)" indicator → `ResumePreview.svelte`

### PDF Export
- [ ] Languages section in classic template → `templates/resume_classic.html`
- [ ] Languages section in modern template → `templates/resume_modern.html`
- [ ] Format: "French - B2" in PDF output → `templates/*.html`

## 4. Test Verification

### API Tests (`tests/test_languages.py`)
- [ ] `test_list_languages_empty` - GET /api/languages returns []
- [ ] `test_add_language` - POST with valid data returns created language
- [ ] `test_add_language_invalid_level` - POST with "X1" returns 422
- [ ] `test_edit_language` - PUT updates name and level
- [ ] `test_delete_language` - DELETE returns {"deleted": id}
- [ ] `test_reorder_languages` - PUT /reorder updates display_order
- [ ] `test_get_nonexistent_language` - GET /9999 returns 404
- [ ] `test_delete_nonexistent_language` - DELETE /9999 returns 404

### Validation Tests
- [ ] All 6 CEFR levels accepted: A1, A2, B1, B2, C1, C2 → `tests/test_languages.py`
- [ ] Empty name rejected with validation error → `tests/test_languages.py`
- [ ] Empty level rejected with validation error → `tests/test_languages.py`

### Integration Tests
- [ ] Languages appear in profile/complete endpoint → `tests/test_languages.py`
- [ ] Languages included in resume content → (manual verification)

## 5. Accessibility Verification

### Keyboard Navigation
- [ ] Tab through all form fields (name, level, save, cancel) → `Languages.svelte`
- [ ] Enter submits form when focused → `Languages.svelte`
- [ ] Escape closes form/dialog → `Languages.svelte`
- [ ] Edit button keyboard accessible → `Languages.svelte`

### Focus Management
- [ ] Focus moves to form when Add clicked → `Languages.svelte`
- [ ] Focus returns to list after save/cancel → `Languages.svelte`
- [ ] Focus trapped in ConfirmDialog → `ConfirmDialog.svelte` (existing)
- [ ] Visible focus indicators on all interactive elements → CSS (existing)

### Form Labels
- [ ] Name input has associated `<label>` with `for` attribute → `Languages.svelte`
- [ ] Level select has associated `<label>` with `for` attribute → `Languages.svelte`
- [ ] Required fields marked with `aria-required="true"` → `Languages.svelte`

### Error Announcements
- [ ] Error messages have `role="alert"` or `aria-live` → `Languages.svelte`
- [ ] Invalid fields have `aria-invalid="true"` → `Languages.svelte`
- [ ] Error messages associated via `aria-describedby` → `Languages.svelte`

### Drag-and-Drop Accessibility
- [ ] Drag handles have `aria-label="Drag to reorder"` → `Languages.svelte`
- [ ] Reorder changes announced via `aria-live` region → `Languages.svelte`
- [ ] Alternative keyboard reorder (optional, nice-to-have) → Future enhancement

### Color Contrast
- [ ] All text meets WCAG 2.1 AA contrast (inherits app theme) → Existing CSS

## 6. Project-Specific Checks

None - no `project-checks.md` found.

## Summary

| Section | Check Count |
|---------|-------------|
| 0. Ecosystem | 3 |
| 1. Dependencies | 3 |
| 2. Syntax | 16 |
| 3. UX | 25 |
| 4. Tests | 11 |
| 5. Accessibility | 15 |
| 6. Project-Specific | 0 |
| **Total** | **73** |

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Checklist review | A - Looks complete | 73 checks approved, no changes needed |
