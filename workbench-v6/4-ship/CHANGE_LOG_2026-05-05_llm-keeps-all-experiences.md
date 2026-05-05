# CHANGE_LOG — llm-keeps-all-experiences

**feature:** llm-keeps-all-experiences  
**date:** 2026-05-05  
**commit_base:** HEAD  
**total_files:** 2  
**total_additions:** +17  
**total_deletions:** -3  

---

## Files by category

### Backend
| file | change_type | +lines | -lines |
|------|-------------|--------|--------|
| services/llm/base.py | M | 7 | 3 |

### Tests
| file | change_type | +lines | -lines |
|------|-------------|--------|--------|
| tests/test_resume_prompts.py | M | 13 | 0 |

---

## Scope drift

**Status:** CLEAN  
**Plan-specified files modified:** 2/2  
**Unplanned files modified:** 0  
**Omitted from plan:** 0  

All changed files appear in the IMPL_PLAN. No drift detected.

---

## Sensitive-area changes

**Status:** CLEAN  

Modified areas:
- `services/llm/base.py`: USER_PROMPT_TEMPLATE (instruction text only; no schema changes, no code logic changes)

This is a prompt-engineering change with no impact on data storage, authentication, or API surfaces. The change restricts the LLM's behavior (forces all work experiences to `included=true`) rather than expanding capability. Low risk.

---

## Suggested commit subject

```
feat: llm returns all work experiences with inclusion toggle in ui
```
