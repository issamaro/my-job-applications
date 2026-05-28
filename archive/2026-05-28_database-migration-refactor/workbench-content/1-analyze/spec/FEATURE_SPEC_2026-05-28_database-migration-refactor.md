# FEATURE_SPEC — database-migration-refactor

**Date:** 2026-05-28 (v5 — reconciled with analysis-reviewer ISSUES round 4)
**Slug:** database-migration-refactor
**Ceremony:** L
**Shape:** Backend-only refactor of `database.py`

## Persona

**Solo maintainer / future-me.** The next time someone adds a column to
`generated_resumes` (or any other table currently touched by a recreate
helper), the refactor must reduce the edit surface from "three places, no
compile-time signal if you miss one" to "two places, named in a checklist."

## Pain point

Hard-coded column lists in `_migrate_skills_unique_constraint` and
`_migrate_generated_resumes_fk_cascade` silently drift from the actual table
shape every time a developer adds a column to the migrations list but forgets
to also update the recreate helper's `CREATE`, `INSERT`, and `SELECT` lists.
Confirmed by `REPRO_2026-05-28_database-migration-refactor.md`: a column
added to the source table but not to the recreate's hardcoded `INSERT/SELECT`
list is dropped — schema and data — when the recreate fires on a fresh
install.

## Definitions

- **Inline DDL block** — the `conn.executescript("""CREATE TABLE IF NOT
  EXISTS ...""")` block at `database.py:270-377`.
- **Legacy `_migrate_*` helpers** — six functions defined at
  `database.py:55-265`. Each has guard logic that no-ops when the
  migration's effect is already present.
- **MIGRATIONS** — the post-refactor `MIGRATIONS: list[tuple[str, str]]`
  module-level constant. Each tuple is `(version_id, sql)`.
- **`schema_versions`** — the post-refactor table tracking which
  `version_id`s have been applied. Single column `version TEXT PRIMARY KEY`
  plus `applied_at TEXT DEFAULT CURRENT_TIMESTAMP`.
- **Current target shape** — the schema produced by an `init_db()` call on
  a fresh DB after this refactor lands. Defined operationally by the post-
  refactor inline DDL block.
- **Effect of an entry** — for an `ALTER TABLE T ADD COLUMN C ...` entry,
  the predicate is "column `C` exists on table `T`" (via
  `PRAGMA table_info(T)`). All post-refactor MIGRATIONS entries target
  current table names (see must-have #5), so the predicate is mechanical.

## Must-have list

1. **Inline DDL produces post-refactor target shape.** Every
   `CREATE TABLE IF NOT EXISTS` in the inline DDL block must produce the
   same shape as a table that has been through every prior `_migrate_*`
   step. After the inline DDL block executes on a fresh install:
   - `skills` has `UNIQUE(user_id, name)` constraint
   - `generated_resumes` has `ON DELETE CASCADE` on its FK to `jobs(id)`,
     uses `job_id` column name (not `job_description_id`), and includes
     `jd_version_id`, `language`, `job_analysis`, `user_id`
   - Every recreate helper's guard predicate (`"user_id" in columns` for
     skills; `"ON DELETE CASCADE" in sql AND has_job_id AND not
     has_job_description_id` for generated_resumes) returns True on the
     first call.

2. **Drop dead inline DDL.** Three `CREATE TABLE IF NOT EXISTS` blocks
   must be removed from the inline DDL:
   - `personal_info` (dropped later at `database.py:500`)
   - `job_descriptions` (renamed to `jobs` at `database.py:438`)
   - `job_description_versions` (renamed to `job_versions` at
     `database.py:440`)
   The post-refactor inline DDL block contains only tables that survive
   `init_db()`. The `jobs` and `job_versions` `CREATE`s currently at
   `database.py:443-455` move into the inline DDL block.

3. **Recreate helpers use dynamic CREATE from PRAGMA + declared
   constraint + declared additions + snapshot-restored indexes.**
   Both `_migrate_skills_unique_constraint` and
   `_migrate_generated_resumes_fk_cascade` rebuild their destination
   CREATE from explicit inputs and preserve any explicit indexes:

   **(a) Primary key column declaration (separate from PRAGMA loop).**
   The destination CREATE begins with `id INTEGER PRIMARY KEY
   [AUTOINCREMENT]`. AUTOINCREMENT presence is detected by regex
   searching the source's `sqlite_master.sql` for the literal phrase
   `INTEGER PRIMARY KEY AUTOINCREMENT` (case-sensitive — SQLite stores
   it as written). The `id` column is **excluded** from the PRAGMA loop
   in step (b); only non-pk source columns iterate through the formula.

   **(b) Non-pk source columns** from `PRAGMA table_info(source)`,
   filtering out rows where `pk=1`. Each remaining row becomes
   `{dst_name} {type}{" NOT NULL" if notnull else ""}{" DEFAULT
   <expr>" if dflt_value else ""}` in the destination CREATE, where
   `dst_name` is the source column name passed through the helper's
   **rename mapping** (an explicit `dict[str, str]`).

   **(c) Additions** — an explicit `list[tuple[str, str]]` of
   `(column_declaration, select_value_sql)` pairs for columns that the
   destination has but the source does not. The `column_declaration`
   is inlined into the destination CREATE; the `select_value_sql` is
   used as a literal expression in the SELECT clause for the column
   position corresponding to that addition.

   **(d) Constraint clause** — appended after all column declarations.

   Per-helper config:
   - `_migrate_skills_unique_constraint`: rename_map=`{}`,
     additions=`[("user_id INTEGER DEFAULT 1", "1")]`,
     constraint=`"UNIQUE(user_id, name)"`.
   - `_migrate_generated_resumes_fk_cascade`: rename_map=
     `{"job_description_id": "job_id"}`, additions=`[]`,
     constraint=`"FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE"`.

   The INSERT/SELECT pair: destination column list (in order) = `[id]`
   ++ (mapped non-pk source names) ++ (addition decl names); SELECT
   clause = `[id]` ++ (source non-pk names) ++ (addition
   select_value_sql).

   **(e) Index preservation.** Before `DROP TABLE source`, snapshot
   every explicit index defined on the source: `SELECT sql FROM
   sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT
   NULL`. (`sql IS NULL` filters out auto-indexes from UNIQUE/PRIMARY KEY
   constraints — those regenerate from the new CREATE TABLE
   automatically.) After `ALTER TABLE source_new RENAME TO source`,
   re-execute each saved SQL string. This preserves
   `idx_generated_resumes_created` and any future explicit indexes
   without requiring per-helper enumeration. (Skills has no explicit
   indexes — the snapshot returns zero rows, the recreate loop no-ops.)

   **Known limitations:** `PRAGMA table_info` exposes `name, type,
   notnull, dflt_value, pk` but not `COLLATE` clauses or generated-column
   expressions. No current recreate-touched table uses these; documented
   in a file-header note, not enforced by tests.

4. **`schema_versions` table.**
   `CREATE TABLE IF NOT EXISTS schema_versions (version TEXT PRIMARY KEY,
   applied_at TEXT DEFAULT CURRENT_TIMESTAMP)`. Created during `init_db()`
   after the legacy `_migrate_*` helpers complete, before the MIGRATIONS
   runner.

5. **MIGRATIONS list shape change.** Convert
   `migrations: list[str]` (currently `database.py:381-409`) into
   `MIGRATIONS: list[tuple[str, str]]` at module scope. Each tuple is
   `(version_id, sql)` where:
   - `version_id` is textual, date-prefixed: e.g.
     `"20240615_jd_title"`, `"20240620_jd_company_name"`,
     `"20260527_breadcrumbs_prompt_path"`. Dates are best-effort
     historical (use commit dates if known, current date otherwise — the
     ordering only matters at the human-readability level; the runner uses
     set membership).
   - `sql` targets **current** table names (post-rename). Specifically:
     - The five entries currently targeting `job_descriptions` are
       rewritten to target `jobs`: `ALTER TABLE jobs ADD COLUMN title
       TEXT DEFAULT 'Untitled Job'`, `... ADD COLUMN company_name TEXT`,
       `... ADD COLUMN updated_at TEXT`, `... ADD COLUMN is_saved
       INTEGER DEFAULT 1`, `... ADD COLUMN user_id INTEGER DEFAULT 1`.
     - The entry currently `ALTER TABLE personal_info ADD COLUMN photo`
       is **deleted** — `personal_info` is dropped from inline DDL, the
       `users.photo` column is already in the post-refactor inline DDL
       for `users`, and the data migration is handled by the
       `_migrate_personal_info_to_users` helper.
     - All other entries (already targeting current names like
       `generated_resumes`, `work_experiences`, etc.) carry over with
       their SQL unchanged.

6. **Fail-loud semantics.** If a MIGRATIONS entry's SQL raises any
   exception during runner execution, the exception propagates from
   `init_db()` to the caller. No swallow: the existing `try/except
   sqlite3.OperationalError: pass` block at `database.py:411-414` is
   removed. The runner MAY wrap the original exception with a
   `try/except` that re-raises (preserving type and chaining) and
   prepends the failing `version_id` to the exception message — this is
   not a swallow and is REQUIRED for Scenario 5's traceback assertion to
   pass. Concrete pattern: `try: conn.execute(sql) except Exception as
   e: raise type(e)(f"[{version_id}] {e}") from e`.

7. **Seeding via mechanical predicate.** On every `init_db()` invocation,
   after `schema_versions` is created (step 4 in execution order below):
   the runner walks `MIGRATIONS` and for each entry whose `version_id` is
   **not yet** in `schema_versions`, computes the predicate from the SQL:
   - Parse `ALTER TABLE <table> ADD COLUMN <column> ...` to extract
     table + column names (a small `re` match — all current entries are
     ADD COLUMN, no other DDL types).
   - If `<column>` is in `PRAGMA table_info(<table>)`, mark the entry
     applied (INSERT into `schema_versions`) without running the SQL.
   - Otherwise, run the SQL and INSERT the row (fail-loud on any
     exception during the SQL).
   This is "seeding" and "runner" in one pass — every invocation. No
   one-time-only logic. Simpler than the v1 spec's separate
   "seed-then-run" step.

8. **Public surface unchanged.** No edits to function signatures consumed
   by external importers. The 17 distinct files importing `database`
   (per `grep -rn "from database\|import database" --include="*.py"`:
   `main.py`, `routes/*.py` × 8, `services/*.py` × 3, `tests/conftest.py`,
   `tests/test_database_migrations.py`, `tests/test_profile_import.py`,
   `tests/test_resume_generator.py`, `tests/test_resumes.py`) continue to
   work without modification. Specifically these symbols remain importable with their
   current shapes:
   - `DATABASE` (str constant)
   - `VALID_TABLES` (frozenset)
   - `init_db() -> None`
   - `get_db() -> contextmanager`
   - `get_or_404(conn, table, id, entity_name, model_class=None)`
   - `exists_or_404(conn, table, id, entity_name)`
   - `fetch_one(conn, table, id, model_class)`

9. **Extend `_migrate_job_description_versions_to_job_versions` to fix
   the legacy index name.** Inside the helper, after the
   `ALTER TABLE job_description_versions RENAME TO job_versions` runs,
   also execute:
   ```
   DROP INDEX IF EXISTS idx_job_description_versions_jd_id;
   CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id);
   ```
   This makes the fresh-install and upgrade-path schemas byte-identical
   under whitespace + sort normalisation (R6 mitigation, see Scenario 2).
   The helper's existing rename gating is unchanged; only the index
   cleanup is added.

10. **Extract `_migrate_personal_info_to_users` from inline if-block.**
    The current inline block at `database.py:478-494` is moved into a new
    helper `_migrate_personal_info_to_users(conn)` with the same gating
    logic (table exists, user with id=1 not yet inserted, personal_info
    has data). The helper joins the legacy `_migrate_*` family. The
    `DROP TABLE IF EXISTS personal_info` at line 500 stays inline,
    positioned after the helper call.

    **Source-column tolerance.** Because the `ALTER TABLE personal_info
    ADD COLUMN photo TEXT` MIGRATIONS entry is deleted (per must-have
    #5), a legacy DB whose `personal_info` predates the photo feature
    would lack the `photo` column. The current code at
    `database.py:489-493` references `photo` in both SELECT and INSERT,
    which would crash on such a DB. The new helper handles this by
    introspecting the source via `PRAGMA table_info(personal_info)`:
    the SELECT and INSERT column lists become the **intersection** of
    `personal_info`'s present columns and the target column set
    (email, full_name, phone, location, linkedin_url, summary, photo,
    updated_at). Any missing column is omitted from both sides — the
    corresponding `users` column takes its default value or NULL.

## Execution order (init_db internals)

The function body runs in this exact order:

```
1. with get_db() as conn:
2.   inline DDL (executescript) — current target shape, no dead CREATEs
3.   legacy _migrate_* helpers in order:
       _migrate_job_descriptions_to_jobs(conn)
       _migrate_raw_text_to_original_text(conn)
       _migrate_job_description_versions_to_job_versions(conn)   # now also fixes index
       _migrate_personal_info_to_users(conn)                     # new helper
       _migrate_skills_unique_constraint(conn)                   # PRAGMA copy + dynamic CREATE
       _migrate_generated_resumes_fk_cascade(conn)               # PRAGMA copy + dynamic CREATE
4.   conn.execute("CREATE TABLE IF NOT EXISTS schema_versions ...")
5.   apply_migrations(conn)   # seeds + runs in one pass per must-have #7
6.   data backfills (kept inline, idempotent):
       UPDATE jobs SET updated_at = created_at WHERE updated_at IS NULL
       UPDATE generated_resumes SET job_analysis = (SELECT parsed_data
         FROM jobs WHERE jobs.id = generated_resumes.job_id)
         WHERE job_analysis IS NULL
7.   conn.execute("DROP TABLE IF EXISTS personal_info")
8.   conn.commit()
```

The order is constrained: (a) inline DDL first so legacy helpers have
tables to act on; (b) legacy helpers before MIGRATIONS runner, so any
legacy DB is renamed to current names before the SQL (which targets
current names) attempts to run; (c) data backfills after both (so
`jobs` and `generated_resumes` exist with `updated_at` and `job_analysis`
columns); (d) `personal_info` DROP at the end, after
`_migrate_personal_info_to_users` had its chance to copy data.

## BDD scenarios

### Scenario 1 — Fresh install produces final shape with no recreates

**Given** `app.db` does not exist on disk
**When** `init_db()` runs
**Then** zero source rows are copied into `*_new` tables — verified by
monkeypatching `_migrate_skills_unique_constraint` and
`_migrate_generated_resumes_fk_cascade` with call-counting wrappers that
still delegate to the originals; both wrappers must register a call but
each must complete via the existing early-return (no `CREATE TABLE
*_new` is observable via `sqlite3.Connection.set_trace_callback` during
their execution).
**And** the `generated_resumes` table's `sqlite_master.sql` contains
`ON DELETE CASCADE`.
**And** the `skills` table's `sqlite_master.sql` contains
`UNIQUE(user_id, name)`.
**And** `schema_versions` contains exactly one row per entry currently
declared in `MIGRATIONS`.
**And** the table column sets (per `PRAGMA table_info`) match the
documented target shape per-table.

**Verification:** `tests/test_database_migrations.py::test_fresh_install_skips_recreates_and_seeds_versions`.

### Scenario 2 — Legacy DB upgrade produces same final shape

**Given** `app.db` is a frozen snapshot of the original 2024 shape:
no CASCADE, no `language` / `job_analysis` / `user_id`,
`job_descriptions` not yet renamed, `skills` with `UNIQUE(name)` (no
`user_id`), with at least one row of seed data in each table to verify
the recreate carries data through
**When** `init_db()` runs once
**Then** every legacy `_migrate_*` helper runs exactly once (verified via
monkeypatched call-counting wrappers).
**And** each MIGRATIONS entry that has not yet been applied to the legacy
DB runs (verified by inspecting `schema_versions` row count after vs
before).
**And** `schema_versions` contains exactly one row per entry currently
declared in `MIGRATIONS`.
**And** when compared against a fresh-install database, both DBs are
**PRAGMA-equivalent**: for every table in `sqlite_master`, both DBs
have the same row from `PRAGMA table_info(<table>)` (column name +
type + notnull + dflt_value + pk match per column), the same row from
`PRAGMA index_list(<table>)` (index name + unique flag), the same row
from `PRAGMA index_info(<index>)` (column membership), and the same
row from `PRAGMA foreign_key_list(<table>)` (from-col + to-table +
to-col + on_delete). Same set of table names in both DBs.

**Verification:**
`tests/test_database_migrations.py::test_upgrade_path_matches_fresh_install`.

### Scenario 3 — Idempotent second boot

**Given** `app.db` already has every migration applied
**When** `init_db()` runs a second time
**Then** zero rows are inserted into `schema_versions`.
**And** zero `ALTER TABLE` or `CREATE TABLE *_new` statements execute
(verified by attaching a `set_trace_callback` for the duration of the
second call and asserting the captured SQL contains neither phrase).
**And** zero exceptions are raised.
**And** the DB is PRAGMA-equivalent (as defined in Scenario 2) to
itself before and after the second call.

**Verification:**
`tests/test_database_migrations.py::test_init_db_idempotent`.

### Scenario 4 — Recreate carries any extra column through

**Given** a connection seeded with a `generated_resumes` table that
includes every currently-declared column plus an extra
`experimental_field TEXT DEFAULT 'present'`, plus the `jobs` table
required for the FK target — and the table's `sqlite_master.sql` does
NOT contain `ON DELETE CASCADE` (forcing the recreate's early-return to
miss)
**When** `_migrate_generated_resumes_fk_cascade(conn)` is called directly
**Then** `PRAGMA table_info(generated_resumes)` includes
`experimental_field` after the helper returns.
**And** any existing row's value in `experimental_field` is preserved
byte-for-byte.
**And** `sqlite_master.sql` for the new table contains
`ON DELETE CASCADE`.

**Verification:**
`tests/test_database_migrations.py::test_recreate_preserves_extra_columns`.

### Scenario 5 — Fail-loud on broken migration

**Given** `MIGRATIONS` is monkeypatched (`monkeypatch.setattr(database,
"MIGRATIONS", [..., ("20999999_broken", "ALTER TABLE doesnotexist ADD
COLUMN x TEXT")])`) AND the entry's column-existence predicate evaluates
False (so the runner attempts the SQL)
**When** `init_db()` runs
**Then** `sqlite3.OperationalError` is raised from `init_db()`.
**And** the version_id `"20999999_broken"` appears in
`traceback.format_exception(exc.__class__, exc, exc.__traceback__)`
(rendered string — this is the single observation channel).
**And** `schema_versions` contains zero rows with version_id
`"20999999_broken"`.

**Verification:**
`tests/test_database_migrations.py::test_failing_migration_fails_loud`.

### Scenario 6 — Pre-existing DB without `schema_versions` is seeded

**Given** an `app.db` that is at current target shape (every column
present, every constraint applied — built by running the post-refactor
`init_db()` once, then `DROP TABLE schema_versions`)
**When** `init_db()` runs
**Then** `schema_versions` is re-created.
**And** `schema_versions` contains exactly one row per entry in
`MIGRATIONS`, all inserted via the mechanical predicate (column already
exists → mark applied without running SQL).
**And** zero `ALTER TABLE` / `CREATE TABLE *_new` statements execute
(verified by `set_trace_callback`).
**And** the DB is PRAGMA-equivalent (as defined in Scenario 2) before
and after.

**Verification:**
`tests/test_database_migrations.py::test_seeds_schema_versions_for_upgraded_db`.

### Scenario 7 — Dead inline CREATEs are gone

**Given** `init_db()` has run on a fresh DB
**When** `sqlite_master` is queried for table names
**Then** `personal_info`, `job_descriptions`, and
`job_description_versions` are absent from the result.

**Verification:**
`tests/test_database_migrations.py::test_dead_tables_absent_after_init`.

### Scenario 8 — personal_info-to-users helper migrates row 1

**Given** an `app.db` seeded with a `personal_info` row at `id = 1`
with the columns the migration historically copies (full_name, email,
phone, location, linkedin_url, summary, photo, updated_at) AND a
`users` table that is empty (no row with `id = 1`)
**When** `init_db()` runs
**Then** the `users` table contains exactly one row with `id = 1` whose
columns match the personal_info source row (full_name, email, phone,
location, linkedin_url, summary, photo).
**And** the `personal_info` table is absent from `sqlite_master` after
`init_db()` returns.

**Verification:**
`tests/test_database_migrations.py::test_personal_info_data_migrates_to_users`.

### Scenario 9 — personal_info-to-users tolerates missing source column

**Given** an `app.db` seeded with a pre-photo `personal_info` row at
`id = 1`: only full_name, email, phone, location, linkedin_url,
summary, updated_at columns exist (no `photo`) AND a `users` table that
is empty (no row with `id = 1`)
**When** `init_db()` runs
**Then** the `users` table contains exactly one row with `id = 1`
whose full_name/email/phone/location/linkedin_url/summary match the
source row.
**And** `users.photo` for that row is NULL (the column exists on
`users` per inline DDL but was not in the source).
**And** zero exceptions are raised.

**Verification:**
`tests/test_database_migrations.py::test_personal_info_helper_tolerates_missing_photo`.

## Success criteria (verifiable)

- All nine BDD scenarios pass as automated tests in
  `tests/test_database_migrations.py`.
- The three existing tests in `tests/test_database_migrations.py`
  (`test_fresh_install_includes_breadcrumb_columns`,
  `test_init_db_idempotent_with_breadcrumb_columns`,
  `test_recreate_path_preserves_breadcrumb_columns`) continue to pass.
- The existing setup-detection test in `tests/test_setup_detection.py`
  continues to pass.
- All other test files (`tests/test_*.py` × 30+) continue to pass via
  the `client` fixture's `init_db()` call.
- Adding a new column to a current target table requires edits to
  exactly two locations in `database.py`: (a) the inline DDL `CREATE
  TABLE <table>` block, (b) one new `(version_id, sql)` tuple appended
  to `MIGRATIONS`. Zero edits to any `_migrate_*` recreate helper.
  Documented as a maintenance contract in the `database.py` file header.

## Out of scope (restating from refined item)

- No Alembic / Yoyo / Diesel. Stdlib `sqlite3` only.
- No rewrite of existing `_migrate_*` gating logic. Only the copy phase
  changes for the two recreate helpers, and the index rename is added
  to one renamed-table helper.
- No row data changes (beyond what backfills already do today).
- No rollback support.
- No table/column renames as part of this refactor.
- Migrations stay in `database.py`.
- No CLI to manage migrations.

## Risk register

| # | Risk | Mitigation |
|---|---|---|
| R1 | Inline DDL now includes `ON DELETE CASCADE` and `UNIQUE(user_id, name)`. On legacy DBs (pre-CASCADE), the inline `CREATE TABLE IF NOT EXISTS` is a no-op (table already exists), so the legacy `_migrate_*` recreate helpers still fire as today. No behavior change on the legacy upgrade path. | Verified by Scenario 2 (upgrade path produces same final shape). |
| R2 | Mechanical predicate (parse `ALTER TABLE T ADD COLUMN C`) is too narrow if a future MIGRATIONS entry uses a different SQL shape (CREATE INDEX, ALTER TABLE RENAME, etc.). | Documented constraint: post-refactor MIGRATIONS entries SHOULD be `ALTER TABLE T ADD COLUMN C ...`. If an entry needs other DDL, the predicate parser must be extended in the same PR. Enforced by Scenario 5's test mechanism: if a non-parseable SQL appears, the predicate returns False conservatively and the SQL is attempted. |
| R3 | `PRAGMA table_info` doesn't expose `COLLATE` clauses, generated-column expressions, or `AUTOINCREMENT`. | AUTOINCREMENT is handled explicitly per must-have #3 (regex check against source `sqlite_master.sql`). COLLATE and generated columns are documented as known limitations in the `database.py` file header. No current recreate-touched table uses COLLATE or generated columns; risk is for future maintainers. |
| R4 | Forgetting to add a `MIGRATIONS` entry when adding a column to inline DDL silently lets fresh installs work but breaks the upgrade path. | Documented in the `database.py` file header as the two-place contract. Scenarios 1 + 2 catch this: a column in inline DDL but missing from MIGRATIONS produces a fresh-install DB without a corresponding `schema_versions` row, AND an upgrade-path DB ends up without that column — the upgrade-vs-fresh byte-identical assertion (Scenario 2) fails. |
| R5 | `PRAGMA foreign_keys = ON` on the connection during the recreate's DROP-and-RENAME phase. Existing code has shipped without explicit transactions. | No behavior change. The recreate's DROP TABLE on `generated_resumes` is OK because no other table FK-references it (it's a referrer, not a referent). |
| R6 | Fresh-vs-upgraded raw `sqlite_master.sql` strings will differ on formatting and on the legacy index name. | The verification mechanism is **PRAGMA equivalence** (defined in Scenario 2), not raw string comparison. This sidesteps formatting/quoting/AUTOINCREMENT-format variance. `_migrate_job_description_versions_to_job_versions` extended (must-have #9) to drop legacy index + create new one so PRAGMA-equivalence isn't broken by the index name mismatch. |
| R7 | Module-level `MIGRATIONS` allows test monkeypatching but also means imports trigger any list-construction errors at import time. | Acceptable. The list is plain tuples of strings — no logic at construction time, no import-time risk. |

## Test plan summary

New file changes: `tests/test_database_migrations.py` gets nine new
tests (Scenarios 1-9). The existing three tests stay. Total: 12 tests
in this file. All in-memory or tempfile, no shared state. Each scenario
covers exactly one behavior.

Existing tests across the suite (30+ files) continue to pass via the
`client` fixture's `setup_test_db()` `init_db()` call — this is the
regression net for must-have #8 (public surface unchanged).
