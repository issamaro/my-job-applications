# Pattern: Enum with Descriptions

**Source:** add-language retrospective
**Date:** 2026-01-07

## Description

Document the pattern used for CEFR levels where:
- Enum values are codes (A1, A2, B1, B2, C1, C2)
- Descriptions shown in dropdown for user guidance ("A1 (Beginner)")
- Only codes displayed in output (resume shows "B2", not "B2 (Upper-Intermediate)")

## Potential Approaches

1. Create a patterns documentation file in docs/
2. Add inline comments in schemas.py as reference
3. Create a code snippet library

## Files Involved

- `schemas.py` - CEFRLevel enum definition
- `Languages.svelte` - Dropdown with descriptions
- `ResumePreview.svelte` - Display with codes only

## Value

Future features needing similar enum patterns (e.g., skill levels, job types) can reference this implementation.
