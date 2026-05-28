# CHANGE_LOG — database-migration-refactor

**Feature:** database-migration-refactor  
**Date:** 2026-05-28  
**Commit base:** HEAD  
**Total files:** 2  
**Total additions:** +821  
**Total deletions:** -362

---

## Files by category

### Backend
| File | Change type | +lines | -lines |
|------|-------------|--------|--------|
| database.py | M | 320 | 355 |

### Tests
| File | Change type | +lines | -lines |
|------|-------------|--------|--------|
| tests/test_database_migrations.py | M | 501 | 7 |

---

## Scope drift

None.

---

## Sensitive-area changes

- **database.py** — Database schema migrations, table recreation helpers, foreign-key CASCADE constraint enforcement on `generated_resumes`, and schema_versions tracking.
- **tests/test_database_migrations.py** — 9 new test cases covering recreate helpers, migration idempotency, dead-table removal, personal_info migration, and upgrade-path equivalence.

All changes are within scope per IMPL_PLAN_2026-05-28_database-migration-refactor.md.

---

## Suggested commit subject

refactor: extract schema migrations into helper functions and add comprehensive test coverage
