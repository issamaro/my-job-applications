feature: database-migration-refactor
date: 2026-05-28
total_checkboxes: 52
derived_from: IMPL_PLAN_2026-05-28_database-migration-refactor.md, FEATURE_SPEC_2026-05-28_database-migration-refactor.md, SQLITE_NOTES_2026-05-28.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Runtime: Python 3.13.9 + SQLite 3.50.4 (confirmed live)"
- [ ] Python constraint matches in `pyproject.toml`: `requires-python = ">=3.13"` (verify: `cat pyproject.toml`)  → source: IMPL_PLAN "Runtime: Python 3.13.9"
- [ ] Virtual environment created and activated (verify: `which python` resolves to `.venv/bin/python` or equivalent)  → source: IMPL_PLAN runtime section

---

## Section 1 — Dependencies

- [ ] `sqlite3` (stdlib) accessible — no manifest entry required; confirm import works: `python -c "import sqlite3; print(sqlite3.sqlite_version)"` prints `3.50.4` or higher  → source: IMPL_PLAN "Runtime: Python 3.13.9 + SQLite 3.50.4"; SQLITE_NOTES "version_constraint: SQLite >= 3.25"
- [ ] `re` (stdlib) accessible — added at top of `database.py` (verify: `grep "^import re" database.py`)  → source: IMPL_PLAN "Imports at top of database.py — Add `import re`"
- [ ] `pytest>=8.0.0` present (verify: `uv tree --package pytest`)  → source: `pyproject.toml` `[dependency-groups] dev`
- [ ] `pytest-asyncio>=0.24.0` present (verify: `uv tree --package pytest-asyncio`)  → source: `pyproject.toml` `[dependency-groups] dev`

---

## Section 2 — Syntax

- [ ] `PRAGMA table_info(<table>)` called with positional table name, result indexed as `row[1]` for name and `row[5]` for pk flag, in `_recreate_table_with_constraint` at `database.py` (verify: `grep "PRAGMA table_info" database.py`)  → source: SQLITE_NOTES §1 "Each row is `(cid, name, type, notnull, dflt_value, pk)`"; IMPL_PLAN `_recreate_table_with_constraint` body
- [ ] `PRAGMA foreign_key_list(<table>)` result compared on `on_delete` (tuple index 6) in `_pragma_equivalent` at `tests/test_database_migrations.py` (verify: `grep "foreign_key_list" tests/test_database_migrations.py`)  → source: SQLITE_NOTES §2 "row is `(id, seq, table, from, to, on_update, on_delete, match)`"; IMPL_PLAN `_pragma_equivalent` helper spec
- [ ] `PRAGMA index_list(<table>)` row filtered on `origin='c'` to detect explicit indexes, in `_pragma_equivalent` at `tests/test_database_migrations.py` (verify: `grep "index_list" tests/test_database_migrations.py`)  → source: SQLITE_NOTES §3 "`origin` — `"c"` = explicit `CREATE INDEX`"
- [ ] `sqlite_master` queried with `type='index' AND tbl_name=? AND sql IS NOT NULL` to snapshot explicit indexes only, in `_recreate_table_with_constraint` at `database.py` (verify: `grep "sql IS NOT NULL" database.py`)  → source: SQLITE_NOTES §4 "`sql IS NOT NULL` for a row where `type = 'index'` reliably indicates an explicit `CREATE [UNIQUE] INDEX`"; IMPL_PLAN `_recreate_table_with_constraint` index snapshot query
- [ ] `connection.set_trace_callback(fn)` called positionally (not as keyword argument) in `tests/test_database_migrations.py` (verify: `grep "set_trace_callback" tests/test_database_migrations.py`)  → source: SQLITE_NOTES §5 "passing the callable by keyword … is deprecated in 3.13 … Use positional form now"; IMPL_PLAN test helpers "`_capture_trace`"
- [ ] `re.search(r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b', sql, re.IGNORECASE)` used (case-insensitive flag present) in `_recreate_table_with_constraint` at `database.py` (verify: `grep -n "IGNORECASE" database.py`)  → source: SQLITE_NOTES §6 "use a case-insensitive regex"; IMPL_PLAN PRAGMA patterns section and `_recreate_table_with_constraint` body
- [ ] `raise type(e)(f"[{version_id}] {e}") from e` pattern used in `_apply_migrations` at `database.py` (verify: `grep "raise type(e)" database.py`)  → source: SQLITE_NOTES §7 "constructs a new instance of that same concrete subclass"; IMPL_PLAN `_apply_migrations` body
- [ ] `sqlite3.version` / `sqlite3.version_info` NOT referenced anywhere in `database.py` or test file (verify: `grep -n "sqlite3\.version[^_]" database.py tests/test_database_migrations.py`)  → source: SQLITE_NOTES "Deprecated to avoid — `sqlite3.version` … removed in Python 3.14"

---

## Section 3 — UX

n/a — no UX_DESIGN source; this is a backend-only refactor.

---

## Section 4 — Tests

### Existing tests (must still pass)

- [ ] `test_fresh_install_includes_breadcrumb_columns` passes (verify: `uv run pytest tests/test_database_migrations.py::test_fresh_install_includes_breadcrumb_columns -v`)  → source: IMPL_PLAN "Keep the existing 3 tests"
- [ ] `test_init_db_idempotent_with_breadcrumb_columns` passes (verify: `uv run pytest tests/test_database_migrations.py::test_init_db_idempotent_with_breadcrumb_columns -v`)  → source: IMPL_PLAN "Keep the existing 3 tests"
- [ ] `test_recreate_path_preserves_breadcrumb_columns` passes (verify: `uv run pytest tests/test_database_migrations.py::test_recreate_path_preserves_breadcrumb_columns -v`)  → source: IMPL_PLAN "Keep the existing 3 tests"

### Test helpers (prerequisites for new tests)

- [ ] `_pragma_equivalent(db_a_path, db_b_path) -> bool` defined in `tests/test_database_migrations.py`, sorts rows before comparison (verify: `grep "_pragma_equivalent" tests/test_database_migrations.py`)  → source: IMPL_PLAN "Test helper utilities — `_pragma_equivalent`"; FEATURE_SPEC Scenario 2 "PRAGMA-equivalent" definition; SQLITE_NOTES §3 note on ordering
- [ ] `_count_calls(monkeypatch, module, attr)` helper defined and returns a `(wrapper_fn, counter_dict)` tuple (verify: `grep "_count_calls" tests/test_database_migrations.py`)  → source: IMPL_PLAN "Test helper utilities — `_count_calls`"
- [ ] `_capture_trace(conn)` context manager defined; calls `set_trace_callback` positionally; unsets on exit (verify: `grep "_capture_trace" tests/test_database_migrations.py`)  → source: IMPL_PLAN "Test helper utilities — `_capture_trace`"; SQLITE_NOTES §5 positional-call requirement
- [ ] `_seed_legacy_2024(db_path)` helper defined; creates pre-CASCADE, pre-rename DB shape with at least one seed row per table (verify: `grep "_seed_legacy_2024" tests/test_database_migrations.py`)  → source: IMPL_PLAN "Test helper utilities — `_seed_legacy_2024`"; FEATURE_SPEC Scenario 2 "frozen snapshot of original 2024 shape"

### Scenario 1 — Fresh install produces final shape with no recreates

- [ ] `test_fresh_install_skips_recreates_and_seeds_versions` present and passes  → source: FEATURE_SPEC Scenario 1; IMPL_PLAN test plan item 1
- [ ] Test monkeypatches both `_migrate_skills_unique_constraint` and `_migrate_generated_resumes_fk_cascade` with call-counting wrappers  → source: FEATURE_SPEC Scenario 1 "monkeypatching `_migrate_*` with call-counting wrappers"
- [ ] Test asserts no `CREATE TABLE *_new` appears in trace during either helper's execution  → source: FEATURE_SPEC Scenario 1 "no `CREATE TABLE *_new` is observable via `set_trace_callback`"
- [ ] Test asserts `generated_resumes` `sqlite_master.sql` contains `ON DELETE CASCADE`  → source: FEATURE_SPEC Scenario 1 "generated_resumes table's `sqlite_master.sql` contains `ON DELETE CASCADE`"
- [ ] Test asserts `skills` `sqlite_master.sql` contains `UNIQUE(user_id, name)`  → source: FEATURE_SPEC Scenario 1 "skills table's `sqlite_master.sql` contains `UNIQUE(user_id, name)`"
- [ ] Test asserts `schema_versions` row count equals `len(database.MIGRATIONS)` (22 rows)  → source: FEATURE_SPEC Scenario 1 "`schema_versions` contains exactly one row per entry … in `MIGRATIONS`"; IMPL_PLAN MIGRATIONS list "22 entries"

### Scenario 2 — Legacy DB upgrade produces same final shape

- [ ] `test_upgrade_path_matches_fresh_install` present and passes  → source: FEATURE_SPEC Scenario 2; IMPL_PLAN test plan item 2
- [ ] Test builds legacy 2024 DB via `_seed_legacy_2024`, calls `init_db()`, then builds a fresh-install DB in a second tempfile  → source: FEATURE_SPEC Scenario 2 "Given `app.db` is a frozen snapshot"
- [ ] Test asserts both DBs are PRAGMA-equivalent via `_pragma_equivalent`  → source: FEATURE_SPEC Scenario 2 "both DBs are PRAGMA-equivalent"

### Scenario 3 — Idempotent second boot

- [ ] `test_init_db_idempotent` present and passes  → source: FEATURE_SPEC Scenario 3; IMPL_PLAN test plan item 3
- [ ] Test captures trace on second `init_db()` call via `_capture_trace`  → source: FEATURE_SPEC Scenario 3 "attaching a `set_trace_callback` for the duration of the second call"
- [ ] Test asserts no `ALTER TABLE` and no `CREATE TABLE` substring in captured trace  → source: FEATURE_SPEC Scenario 3 "zero `ALTER TABLE` or `CREATE TABLE *_new` statements execute"
- [ ] Test asserts `schema_versions` row count unchanged after second call  → source: FEATURE_SPEC Scenario 3 "zero rows are inserted into `schema_versions`"
- [ ] Test asserts PRAGMA-equivalence before and after second call  → source: FEATURE_SPEC Scenario 3 "DB is PRAGMA-equivalent … before and after the second call"

### Scenario 4 — Recreate carries any extra column through

- [ ] `test_recreate_preserves_extra_columns` present and passes  → source: FEATURE_SPEC Scenario 4; IMPL_PLAN test plan item 4
- [ ] Test seeds `generated_resumes` with `experimental_field TEXT DEFAULT 'preserved'` column and a row, without `ON DELETE CASCADE` in DDL  → source: FEATURE_SPEC Scenario 4 "table … does NOT contain `ON DELETE CASCADE` (forcing the recreate's early-return to miss)"
- [ ] Test calls `_migrate_generated_resumes_fk_cascade(conn)` directly  → source: FEATURE_SPEC Scenario 4 "call helper directly"
- [ ] Test asserts `experimental_field` present in `PRAGMA table_info` after helper returns  → source: FEATURE_SPEC Scenario 4 "`PRAGMA table_info(generated_resumes)` includes `experimental_field`"
- [ ] Test asserts seed row value for `experimental_field` is preserved byte-for-byte  → source: FEATURE_SPEC Scenario 4 "existing row's value … preserved byte-for-byte"

### Scenario 5 — Fail-loud on broken migration

- [ ] `test_failing_migration_fails_loud` present and passes  → source: FEATURE_SPEC Scenario 5; IMPL_PLAN test plan item 5
- [ ] Test monkeypatches `MIGRATIONS` to append `("20999999_broken", "ALTER TABLE doesnotexist ADD COLUMN x TEXT")`  → source: FEATURE_SPEC Scenario 5 "`MIGRATIONS` is monkeypatched"
- [ ] Test asserts `sqlite3.OperationalError` is raised from `init_db()`  → source: FEATURE_SPEC Scenario 5 "`sqlite3.OperationalError` is raised from `init_db()`"
- [ ] Test asserts `"20999999_broken"` appears in `traceback.format_exception(...)` rendered string  → source: FEATURE_SPEC Scenario 5 "version_id `20999999_broken` appears in `traceback.format_exception`"
- [ ] Test asserts no `schema_versions` row with `version_id = "20999999_broken"`  → source: FEATURE_SPEC Scenario 5 "`schema_versions` contains zero rows with that version_id"

### Scenario 6 — Pre-existing DB without `schema_versions` is seeded

- [ ] `test_seeds_schema_versions_for_upgraded_db` present and passes  → source: FEATURE_SPEC Scenario 6; IMPL_PLAN test plan item 6
- [ ] Test drops `schema_versions` after first `init_db()`, then calls `init_db()` again  → source: FEATURE_SPEC Scenario 6 "`DROP TABLE schema_versions`"
- [ ] Test asserts `schema_versions` exists after second call with row count equal `len(database.MIGRATIONS)`  → source: FEATURE_SPEC Scenario 6 "`schema_versions` is re-created … exactly one row per entry"
- [ ] Test asserts no `ALTER TABLE` or `CREATE TABLE *_new` in trace during second call  → source: FEATURE_SPEC Scenario 6 "zero `ALTER TABLE` / `CREATE TABLE *_new` statements execute"

### Scenario 7 — Dead inline CREATEs are gone

- [ ] `test_dead_tables_absent_after_init` present and passes  → source: FEATURE_SPEC Scenario 7; IMPL_PLAN test plan item 7
- [ ] Test asserts `personal_info` absent from `sqlite_master` after `init_db()`  → source: FEATURE_SPEC Scenario 7
- [ ] Test asserts `job_descriptions` absent from `sqlite_master` after `init_db()`  → source: FEATURE_SPEC Scenario 7
- [ ] Test asserts `job_description_versions` absent from `sqlite_master` after `init_db()`  → source: FEATURE_SPEC Scenario 7

### Scenario 8 — personal_info data migrates to users

- [ ] `test_personal_info_data_migrates_to_users` present and passes  → source: FEATURE_SPEC Scenario 8; IMPL_PLAN test plan item 8
- [ ] Test seeds `personal_info` row at `id=1` with all 8 columns including `photo`; `users` table empty  → source: FEATURE_SPEC Scenario 8 "seeded with a `personal_info` row at `id = 1` … (full_name, email, phone, location, linkedin_url, summary, photo, updated_at)"
- [ ] Test asserts `users` row `id=1` column values match source row  → source: FEATURE_SPEC Scenario 8 "`users` table contains exactly one row with `id = 1`"
- [ ] Test asserts `personal_info` absent from `sqlite_master` after `init_db()` returns  → source: FEATURE_SPEC Scenario 8 "`personal_info` table is absent from `sqlite_master`"

### Scenario 9 — personal_info-to-users tolerates missing photo column

- [ ] `test_personal_info_helper_tolerates_missing_photo` present and passes  → source: FEATURE_SPEC Scenario 9; IMPL_PLAN test plan item 9
- [ ] Test seeds `personal_info` without `photo` column; `users` empty  → source: FEATURE_SPEC Scenario 9 "only full_name, email, phone, location, linkedin_url, summary, updated_at columns exist (no `photo`)"
- [ ] Test asserts `users` row `id=1` has matching text fields  → source: FEATURE_SPEC Scenario 9 "full_name/email/phone/location/linkedin_url/summary match"
- [ ] Test asserts `users.photo` is NULL for that row  → source: FEATURE_SPEC Scenario 9 "`users.photo` for that row is NULL"
- [ ] Test asserts no exception raised  → source: FEATURE_SPEC Scenario 9 "zero exceptions are raised"

### Regression net

- [ ] Full suite passes: `uv run pytest` exits 0 (covers 30+ test files exercising `init_db()` via `setup_test_db` fixture)  → source: IMPL_PLAN "Run `uv run pytest` full suite for regression check"; FEATURE_SPEC must-have #8 "public surface unchanged"

### Direct source-level structural checks

- [ ] `init_db()` body in `database.py` calls helpers in this exact order: `executescript(_INLINE_DDL)`, `_migrate_job_descriptions_to_jobs`, `_migrate_raw_text_to_original_text`, `_migrate_job_description_versions_to_job_versions`, `_migrate_personal_info_to_users`, `_migrate_skills_unique_constraint`, `_migrate_generated_resumes_fk_cascade`, `_apply_migrations`. Verify by reading the function body  → source: FEATURE_SPEC execution order (must-haves #1-#10 all assume this order); IMPL_PLAN init_db reorder section
- [ ] `idx_job_versions_job_id` exists post-init and `idx_job_description_versions_jd_id` is absent. Verify via test asserting both conditions on a freshly-initialised DB (separate from the legacy upgrade path)  → source: FEATURE_SPEC must-have #9; IMPL_PLAN extension of `_migrate_job_description_versions_to_job_versions`
- [ ] No `try/except sqlite3.OperationalError: pass` blocks remain in `database.py` (grep returns 0 hits for `except sqlite3.OperationalError: pass`)  → source: FEATURE_SPEC must-have #6 "the existing try/except swallow block is removed"
- [ ] Inline DDL block has no `CREATE TABLE IF NOT EXISTS personal_info`, no `CREATE TABLE IF NOT EXISTS job_descriptions`, no `CREATE TABLE IF NOT EXISTS job_description_versions` (grep within `_INLINE_DDL` or executescript block returns 0 hits for each)  → source: FEATURE_SPEC must-have #2 "drop dead inline DDL"

---

## Section 5 — Accessibility

n/a — no UX_DESIGN source; this is a backend-only refactor.
