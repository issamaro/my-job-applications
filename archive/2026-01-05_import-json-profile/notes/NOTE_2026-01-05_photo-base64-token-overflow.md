# Note: Profile Photo Causing LLM Token Overflow

**Date:** 2026-01-05
**Category:** LEARNING
**During:** Bug fix for resume generation failure

---

## What Happened

Resume generation was failing with a generic "Could not generate resume" error. After adding logging, discovered the actual error was `prompt is too long: 212002 tokens > 200000 maximum`.

## Context

- **File(s):** `services/resume_generator.py`, `services/llm.py`
- **Expected:** Job description (~6800 chars) + profile data should be ~5K tokens total
- **Actual:** Prompt was 212K tokens due to base64-encoded profile photo (1.3MB / ~335K tokens)

---

## Resolution

Excluded the `photo` field from the profile dict before sending to the LLM:

```python
# services/resume_generator.py
if profile_dict.get("personal_info") and "photo" in profile_dict["personal_info"]:
    del profile_dict["personal_info"]["photo"]
```

Also:
- Increased `max_tokens` from 4096 to 8192 for safety margin
- Added error logging to surface actual API errors
- Updated frontend to show actual error messages instead of generic fallback

---

## Impact

- **Immediate:** Resume generation now works with any profile photo size
- **Future:** No - fix is complete
- **Checklist:** Yes - add "Never send binary/base64 data to LLM endpoints" as a check

---

## Key Learning

When sending profile/user data to LLMs, always audit what fields are included. Base64-encoded images can easily exceed context limits (1MB image = ~1.3MB base64 = ~335K tokens).

---

*Captured during resume generation bug fix*
