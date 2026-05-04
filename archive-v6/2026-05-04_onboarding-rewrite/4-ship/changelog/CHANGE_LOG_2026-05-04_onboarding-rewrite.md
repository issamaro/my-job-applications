---
feature: onboarding-rewrite
date: 2026-05-04
commit_base: HEAD
total_files: 3
total_additions: 450
total_deletions: 106
---

# Change Log — Onboarding Rewrite

## Files by category

### Docs
| File | Change type | +lines | −lines |
|------|-------------|--------|--------|
| README.md | M | 104 | 46 |

### Config
| File | Change type | +lines | −lines |
|------|-------------|--------|--------|
| dev.sh | M | 8 | 16 |

### Other
| File | Change type | +lines | −lines |
|------|-------------|--------|--------|
| setup.sh | M | 338 | 44 |

## Scope drift

None. All three modified files are in IMPL_PLAN's "Files to modify" list. No unplanned files were changed. No explicit non-changes were violated.

## Sensitive-area changes

None. Modifications do not touch auth config, db schema, or public API definitions. Changes are isolated to:
- User-facing documentation (README)
- Local setup scripts (setup.sh, dev.sh)
- No changes to `services/llm/`, `app/`, `frontend/`, `tests/`, `pyproject.toml`, `package.json`

## Suggested commit subject

feat: interactive onboarding flow with atomic shell-rc writes and improved documentation
