# Data Flow Documentation

**Source:** european-cv-templates retrospective
**Date:** 2026-01-08
**Type:** Documentation / Process Improvement

---

## Description

During the European CV Templates feature, we discovered that assumptions about data availability didn't account for mid-pipeline transformations. The photo field was "available" but got stripped for LLM calls and never restored.

**Lesson:** Document data flow for complex fields that are modified during processing.

---

## Problem

When implementing European templates, the profile photo wasn't appearing even though:
- It was correctly stored in `personal_info.photo`
- It was correctly flagged as "excluded from LLM calls"
- Tests verified it existed

The issue: after stripping for LLM, it was never restored before saving to resume_content.

---

## Suggested Approach

Create a `docs/DATA_FLOW.md` document that traces how key data moves through the system:

1. **Profile Photo Flow**
   - Stored: `personal_info.photo` (base64 data URL)
   - Read: `profile_service.get_complete()`
   - Stripped: `resume_generator.generate()` (for LLM payload)
   - Restored: Must explicitly save and restore after LLM call
   - Final: `resume_content.personal_info.photo`

2. **Other Complex Fields** (if applicable)
   - Languages (filtered by included flag)
   - Work experiences (filtered, reordered)

---

## Potential Benefits

- Prevent similar bugs in future features
- Help new contributors understand data transformations
- Serve as debugging reference

---

## Priority

LOW - Documentation improvement, not blocking any feature

---

*Created from european-cv-templates retrospective*
