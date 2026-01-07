# Implementation Plan: Add Language Section

**Date:** 2026-01-07
**Feature:** add-language
**Sources:**
- `workbench/1-analyze/requirements/FEATURE_SPEC_2026-01-07_add-language.md`
- `workbench/1-analyze/ux/UX_DESIGN_2026-01-07_add-language.md`
- `workbench/2-plan/research/LIBRARY_NOTES_2026-01-07_add-language.md`

## Affected Files

### Backend Files

| File | Change | Description |
|------|--------|-------------|
| `database.py` | Modify | Add `languages` table with CEFR CHECK constraint |
| `schemas.py` | Modify | Add Language, LanguageCreate, LanguageUpdate, CEFRLevel, ResumeLanguage schemas |
| `routes/languages.py` | Create | New router with CRUD + reorder endpoints |
| `main.py` | Modify | Import and register languages router |
| `services/resume_generator.py` | Modify | Include languages in resume content |
| `services/profile.py` | Modify | Include languages in complete profile |

### Frontend Files

| File | Change | Description |
|------|--------|-------------|
| `src/lib/api.js` | Modify | Add language CRUD + reorder API functions |
| `src/components/Languages.svelte` | Create | New component with drag-drop reordering |
| `src/components/ProfileEditor.svelte` | Modify | Add Languages section |
| `src/components/ResumePreview.svelte` | Modify | Add Languages ResumeSection with toggle |
| `src/components/PdfPreview.svelte` | Modify | Add Languages section (if applicable) |

### Template Files

| File | Change | Description |
|------|--------|-------------|
| `templates/resume_classic.html` | Modify | Add Languages section |
| `templates/resume_modern.html` | Modify | Add Languages section |

### Test Files

| File | Change | Description |
|------|--------|-------------|
| `tests/test_languages.py` | Create | CRUD + validation + reorder tests |

## Selected Approach

**Single approach** - Follow existing codebase patterns exactly:
- Database: SQLite with CHECK constraint (matches skills/education pattern)
- Backend: FastAPI router with Pydantic validation (matches education.py)
- Frontend: Svelte 5 component with $state/$effect (matches Education.svelte)
- Drag-drop: Native HTML5 API (no external library needed)

No alternative approaches considered necessary.

## Database Changes

```sql
-- In database.py init_db()
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Approach

### Service Pattern
No dedicated service needed - direct database access in routes (matches education.py pattern).

### Validation Approach
1. **Backend (Pydantic):** `CEFRLevel(str, Enum)` validates level field
2. **Backend (SQLite):** CHECK constraint as fallback
3. **Frontend:** Native `<select>` restricts to valid options

### Error Handling Strategy
Follow existing patterns:
- 404: Resource not found
- 422: Validation error (automatic from Pydantic)
- Generic error messages to frontend: "Could not save/delete. Please try again."

## Implementation Order

### Step 1: Database Schema
**File:** `database.py:init_db`
- Add `languages` table CREATE statement after `projects` table
- Fields: id, name, level (with CHECK), display_order, created_at, updated_at

### Step 2: Pydantic Schemas
**File:** `schemas.py`
- Add `CEFRLevel(str, Enum)` enum class (~line 3)
- Add `LanguageCreate` schema with name (str), level (CEFRLevel)
- Add `LanguageUpdate` schema (same fields)
- Add `Language` response schema with id, name, level, display_order, timestamps
- Add `ResumeLanguage` schema with name, level, included fields
- Update `ResumeContent` to include `languages: list[ResumeLanguage] = []`
- Add `LanguageImport` schema for profile import
- Update `ProfileImport` to include `languages: list[LanguageImport] = []`

### Step 3: API Routes
**File:** `routes/languages.py` (new)
- `GET /api/languages` → list[Language] ordered by display_order
- `POST /api/languages` → Language (auto-assign display_order = max + 1)
- `PUT /api/languages/{lang_id}` → Language
- `DELETE /api/languages/{lang_id}` → {"deleted": id}
- `PUT /api/languages/reorder` → list[Language] (accepts list of {id, display_order})

### Step 4: Register Router
**File:** `main.py`
- Import `from routes import languages` (~line 9)
- Add `app.include_router(languages.router)` (~line 34)

### Step 5: Update Profile Service
**File:** `services/profile.py`
- Add languages to `get_complete()` method
- Query languages table, include in CompleteProfile response

### Step 6: Frontend API Functions
**File:** `src/lib/api.js`
- Add `getLanguages()` → GET /languages
- Add `createLanguage(data)` → POST /languages
- Add `updateLanguage(id, data)` → PUT /languages/{id}
- Add `deleteLanguage(id)` → DELETE /languages/{id}
- Add `reorderLanguages(items)` → PUT /languages/reorder

### Step 7: Languages Component
**File:** `src/components/Languages.svelte` (new)
- Follow Education.svelte structure
- State: items, loading, error, editingId, showForm, saving, saved, confirmDelete, fieldErrors
- Form: name input (required), level select (CEFR dropdown with descriptions)
- List: draggable items with drag handles (⋮⋮)
- Drag-drop: native HTML5 ondragstart/ondragover/ondrop
- Functions: loadData, add, edit, cancel, validate, save, requestDelete, confirmDeleteAction, handleDragStart, handleDragOver, handleDrop

### Step 8: Profile Editor Integration
**File:** `src/components/ProfileEditor.svelte`
- Import Languages component
- Add `languagesRef` state
- Add Languages Section after Skills section

### Step 9: Resume Integration - Schemas
**File:** `services/resume_generator.py`
- Update `_row_to_response()` to include languages
- Update `ResumeContent` instantiation with languages field

### Step 10: Resume Preview
**File:** `src/components/ResumePreview.svelte`
- Add `toggleSection('languages')` case
- Add Languages ResumeSection after Education
- Display format: "{name} - {level}" for each language

### Step 11: PDF Templates
**Files:** `templates/resume_classic.html`, `templates/resume_modern.html`
- Add Languages section:
```html
{% if languages %}
<section class="languages">
    <h2>Languages</h2>
    {% for lang in languages %}
    <span>{{ lang.name }} - {{ lang.level }}{% if not loop.last %}, {% endif %}</span>
    {% endfor %}
</section>
{% endif %}
```

### Step 12: Profile Import
**File:** `routes/profile_import.py`
- Add languages handling in import route
- Insert with sequential display_order

### Step 13: Tests
**File:** `tests/test_languages.py` (new)
- `test_list_languages_empty` - GET returns []
- `test_add_language` - POST with valid CEFR level
- `test_add_language_invalid_level` - POST with "X1" returns 422
- `test_edit_language` - PUT updates name/level
- `test_delete_language` - DELETE removes and returns {"deleted": id}
- `test_reorder_languages` - PUT /reorder updates display_order
- `test_get_nonexistent_language` - GET /9999 returns 404

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Drag-drop not working on mobile | Medium | Medium | Use touch events as fallback, test on mobile browsers |
| CEFR validation bypass | Low | Low | CHECK constraint at DB level provides defense in depth |
| Display order conflicts on concurrent edits | Low | Low | Single user app, no concurrent access expected |
| Resume generation ignoring languages | Low | Medium | Add languages to LLM prompt context in future iteration |

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Approach selection | N/A | Single approach following existing patterns |
| Plan review | A - Looks good | 8-step implementation order approved |

## Dependencies Summary

**No new dependencies required.**

All functionality implemented with existing stack:
- Python 3.13 + FastAPI + Pydantic 2
- Svelte 5 + Native HTML5 Drag-Drop API
- SQLite

## Next

Proceed to `/v5-checklist`
