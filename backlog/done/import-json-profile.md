# Import JSON Profile - SCOPED_FEATURE

**Size:** M (Medium)
**Scoped:** 2026-01-04
**Files affected:** ~6-8
**Dependencies:** None
**Ready for:** /v4-feature

---

## Description

Allow users to import their complete profile data from a JSON file. This enables users to use external AI tools (like ChatGPT, Claude) to generate a well-structured profile JSON, then simply import it into the platform. On import, existing profile data is replaced except for the profile picture, which is preserved.

## Scope (IN)

- JSON file upload UI in the ProfileEditor area
- JSON schema validation before import
- Bulk replacement of profile data via API:
  - Personal info (excluding photo)
  - Work experiences (clear all, then add new)
  - Education (clear all, then add new)
  - Skills (clear all, then add new)
  - Projects (clear all, then add new)
- Preserve existing profile picture during import
- User confirmation before destructive import ("This will replace all existing data except your photo")
- Error handling with clear messages for invalid JSON
- Sample JSON schema documentation (for AI prompt reference)

## Out of Scope (NOT)

- JSON export functionality (separate feature)
- Partial/merge import (this is full replacement only)
- Profile picture import via JSON (photos remain separate)
- Validation of URL formats, email formats (rely on existing field validations)
- Undo/rollback after import
- Import from URL (file upload only)

## Success Criteria

- [ ] User can upload a `.json` file containing profile data
- [ ] Invalid JSON shows clear error message without affecting existing data
- [ ] Valid JSON with wrong schema shows specific validation errors
- [ ] Successful import replaces all profile sections (personal info, work, education, skills, projects)
- [ ] Profile picture is NOT deleted or modified during import
- [ ] User sees confirmation dialog before import executes
- [ ] After successful import, ProfileEditor displays the new data
- [ ] Sample JSON schema is documented for users/AI reference

## JSON Schema Reference

```json
{
  "personal_info": {
    "full_name": "string (required)",
    "email": "string (required)",
    "phone": "string (optional)",
    "location": "string (optional)",
    "linkedin_url": "string (optional)",
    "summary": "string (optional)"
  },
  "work_experiences": [
    {
      "company": "string (required)",
      "title": "string (required)",
      "location": "string (optional)",
      "start_date": "YYYY-MM (required)",
      "end_date": "YYYY-MM or null (optional)",
      "is_current": "boolean",
      "description": "string (optional)"
    }
  ],
  "education": [
    {
      "institution": "string (required)",
      "degree": "string (required)",
      "field_of_study": "string (optional)",
      "graduation_year": "number (optional)",
      "gpa": "number (optional)",
      "notes": "string (optional)"
    }
  ],
  "skills": [
    { "name": "string (required)" }
  ],
  "projects": [
    {
      "name": "string (required)",
      "description": "string (optional)",
      "technologies": "string (optional)",
      "url": "string (optional)",
      "start_date": "YYYY-MM (optional)",
      "end_date": "YYYY-MM (optional)"
    }
  ]
}
```

## Notes

- The photo is stored at a separate API endpoint (`/api/photos`) and is NOT part of the profile import/export flow
- Backend will need a new bulk import endpoint (e.g., `POST /api/profile/import`) that handles transactional replacement
- Consider adding a "Download Sample JSON" button to help users understand the expected format
- This feature complements a future "Export JSON" feature for full profile portability
