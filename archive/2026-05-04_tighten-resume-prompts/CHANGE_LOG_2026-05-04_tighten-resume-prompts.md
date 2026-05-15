## Change Log: tighten-resume-prompts

**feature:** tighten-resume-prompts  
**date:** 2026-05-04  
**commit_base:** HEAD (5313105)  
**total_files:** 2  
**total_additions:** +23  
**total_deletions:** −2  

---

## Files by category

### Backend

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| services/llm/base.py | M | 16 | 2 |

### Tests

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| tests/test_resume_prompts.py | A | 7 | 0 |

### Frontend

(none)

### Config

(none)

### Docs

(none)

### Other

(none)

---

## Scope drift

**Unplanned changes:** none  
**Omitted from plan:** none  
**Status:** CLEAN — all changes align with refined backlog item (Scope IN).

---

## Sensitive-area changes

**Auth / DB schema / public-API surface / security config:** none  
**Status:** CLEAN

---

## Suggested commit subject

```
feat(prompts): cap resume summary/descriptions at 350 chars and enforce first-person voice
```
