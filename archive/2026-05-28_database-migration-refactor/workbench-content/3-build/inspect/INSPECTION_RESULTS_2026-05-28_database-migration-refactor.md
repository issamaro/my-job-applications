feature: database-migration-refactor
date: 2026-05-28
status: READY
playwright: skipped

---

## Playwright

skipped — backend-only refactor, no UI surface, no dev_server_url supplied.

---

## Test results (pre-verified)

282 passed, 0 failed (exit code 0, duration 28.21s).
Source: TEST_RESULTS_2026-05-28_database-migration-refactor.md

---

## Manual checklist

The bullets below are code-level structural checks a human can verify by
reading database.py, running short grep commands, or booting the app once.
No UI interaction required.

- Open `database.py` and read `init_db()` (line 440 onward). Confirm the body calls helpers in this exact order: `executescript(_INLINE_DDL)`, `_migrate_job_descriptions_to_jobs`, `_migrate_raw_text_to_original_text`, `_migrate_job_description_versions_to_job_versions`, `_migrate_personal_info_to_users`, `_migrate_skills_unique_constraint`, `_migrate_generated_resumes_fk_cascade`, `_migrate_apply_pending`. No other calls should appear between them.
- Run `grep -n "except sqlite3.OperationalError: pass" database.py` — confirm zero hits (the old swallow block is gone).
- Run `grep -n "CREATE TABLE IF NOT EXISTS personal_info\|CREATE TABLE IF NOT EXISTS job_descriptions\|CREATE TABLE IF NOT EXISTS job_description_versions" database.py` — confirm zero hits (dead inline DDL removed).
- Run `grep -n "_migrate_" database.py` and confirm every helper is invoked exactly once inside `init_db()`, with no dangling call sites elsewhere in the file.
- Run `grep -n "raise type(e)" database.py` — confirm exactly one hit, inside `_migrate_apply_pending`, matching the pattern `raise type(e)(f"[{version_id}] {e}") from e`.
- Run `grep -n "IGNORECASE" database.py` — confirm at least one hit inside `_migrate_recreate_with_constraint`, covering the AUTOINCREMENT regex check.
- Run `grep -n "sql IS NOT NULL" database.py` — confirm at least one hit inside `_migrate_recreate_with_constraint`, used in the `sqlite_master` index-snapshot query.
- Run `grep -n "import re" database.py` — confirm `import re` appears at the top of the file (not inside a function).
- Run `uv run uvicorn main:app --reload` and confirm the server reaches "Application startup complete." without any traceback. Then Ctrl-C to stop.

---

## Decisions

none — parent collects user verdict
