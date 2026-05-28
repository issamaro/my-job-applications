# IMPL_PLAN — database-migration-refactor

**Date:** 2026-05-28
**Slug:** database-migration-refactor
**Ceremony:** L
**Runtime:** Python 3.13.9 + SQLite 3.50.4 (confirmed live)
**Spec:** FEATURE_SPEC v5

## Files to touch

| Path | Action | Approx. effort |
|------|--------|-----------------|
| `database.py` | Modify (heavy) | the whole refactor lives here |
| `tests/test_database_migrations.py` | Modify (extend) | 9 new tests; keep existing 3 |

No other files change. The 17 importers of `database` keep their imports — only `init_db()`, `get_db()`, the helpers, and constants are exposed, all signatures preserved (must-have #8).

## Library patterns (cited from SQLITE_NOTES_2026-05-28.md + live verification)

- `PRAGMA table_info(<table>)` returns tuples `(cid, name, type, notnull, dflt_value, pk)`. `notnull=0` and `dflt_value=None` on `INTEGER PRIMARY KEY AUTOINCREMENT` — PRAGMA can't distinguish AUTO from plain PK.
- `PRAGMA foreign_key_list(<table>)` returns `(id, seq, table, from, to, on_update, on_delete, match)`. Use `on_delete` for CASCADE comparison.
- `PRAGMA index_list(<table>)` returns `(seq, name, unique, origin, partial)`. `origin='c'` = explicit `CREATE INDEX`; `origin='u'` = UNIQUE auto-index; `origin='pk'` = PRIMARY KEY auto-index.
- `PRAGMA index_info(<index>)` returns `(seqno, cid, name)`.
- `sqlite_master` rows: `type='index' AND tbl_name=? AND sql IS NOT NULL` filters explicit indexes only (auto-indexes have `sql IS NULL`).
- `sqlite_master.sql` preserves verbatim user-written case → use case-insensitive regex for AUTOINCREMENT detection: `re.search(r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b', sql, re.IGNORECASE)`.
- `Connection.set_trace_callback(fn)` captures DDL+DML; pass `None` to unset. Keyword arg deprecated in 3.13, positional-only in 3.15 — call positionally.
- `raise type(e)(f"[ctx] {e}") from e` preserves subclass identity (`isinstance(new, sqlite3.OperationalError)` remains True).

## Symbol-by-symbol plan for `database.py`

### Existing constants (keep)

- `DATABASE`, `VALID_TABLES` — unchanged.

### Existing public helpers (keep, signatures unchanged)

- `get_or_404`, `exists_or_404`, `fetch_one`, `get_db` — no edits.

### Inline DDL block at `init_db()` (lines 270-377 today) → REWRITE

Remove these `CREATE TABLE IF NOT EXISTS` blocks entirely (must-have #2):

- `personal_info` (line 271-281)
- `job_descriptions` (line 347-352)

Update these to current target shape:

- `skills` (line 321-324) — change to:
  ```
  CREATE TABLE IF NOT EXISTS skills (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      user_id INTEGER DEFAULT 1,
      UNIQUE(user_id, name)
  );
  ```
- `generated_resumes` (line 354-373) — change to the post-CASCADE shape with all columns from the post-history state. FK column is `job_id`, references `jobs(id)`, with `ON DELETE CASCADE`. Includes `jd_version_id`, `language`, `job_analysis`, `user_id`, plus the 9 breadcrumb columns (already present). FK declared at the end.

Move into the inline DDL block (currently outside at lines 422-455):

- `job_versions` CREATE (line 444-455) → moves into inline DDL block. With `idx_job_versions_job_id` index.

The `job_description_versions` CREATE at line 423-434 is removed entirely (must-have #2 — it's renamed to `job_versions`; the inline block now creates `job_versions` directly).

Existing tables left untouched in inline DDL:

- `users`, `work_experiences`, `education`, `projects`, `languages`, `jobs` (the `jobs` table is currently NOT in inline DDL — it gets renamed from `job_descriptions`. After this refactor, `jobs` IS in inline DDL with its full current shape including all post-history columns: `title`, `company_name`, `updated_at`, `is_saved`, `user_id`, `original_text`, `parsed_data`, `created_at`).

**Indexes in the inline DDL block** (explicit, must be preserved by the
rewrite):

- `CREATE INDEX IF NOT EXISTS idx_generated_resumes_created ON generated_resumes(created_at DESC);`
- `CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id);`

Both indexes are part of `_INLINE_DDL`. Without them, fresh installs
would diverge from upgraded DBs (which restore them via the recreate
helper's index snapshot/replay).

### `_migrate_skills_unique_constraint` (line 55-91) → REFACTOR

Replace the hardcoded `CREATE skills_new` and hardcoded `INSERT/SELECT` with calls into the new shared helper. Keep the existing guard: `if "user_id" in columns: return`. The function body becomes:

```python
def _migrate_skills_unique_constraint(conn):
    cursor = conn.execute("PRAGMA table_info(skills)")
    columns = [row[1] for row in cursor.fetchall()]
    if "user_id" in columns:
        return
    _recreate_table_with_constraint(
        conn,
        source_table="skills",
        rename_map={},
        additions=[("user_id INTEGER DEFAULT 1", "1")],
        constraint_clause="UNIQUE(user_id, name)",
    )
```

### `_migrate_generated_resumes_fk_cascade` (line 182-265) → REFACTOR

Same pattern. Keep the existing CASCADE+columns guard (line 195-200). The function body becomes:

```python
def _migrate_generated_resumes_fk_cascade(conn):
    cursor = conn.execute("PRAGMA table_info(generated_resumes)")
    columns = [row[1] for row in cursor.fetchall()]
    has_job_id = "job_id" in columns
    has_job_description_id = "job_description_id" in columns
    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    )
    row = cursor.fetchone()
    if row and "ON DELETE CASCADE" in (row[0] or "") and has_job_id and not has_job_description_id:
        return
    rename_map = {} if has_job_id else {"job_description_id": "job_id"}
    _recreate_table_with_constraint(
        conn,
        source_table="generated_resumes",
        rename_map=rename_map,
        additions=[],
        constraint_clause="FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE",
    )
```

### NEW shared helper `_recreate_table_with_constraint` (added near other migration helpers)

Implements the five-input recreate algorithm from must-have #3.

**Helper assumptions (documented at the call site):** the source table has
a single primary key column literally named `id` with declared type
`INTEGER`. Both current callers (`skills`, `generated_resumes`) satisfy
this. If a future caller has a different pk shape (composite, non-INTEGER,
non-`id` name), the helper must be extended. This assumption is captured
in the file-header limitations note alongside COLLATE / generated-column.

```python
def _recreate_table_with_constraint(conn, source_table, rename_map, additions, constraint_clause):
    pragma_rows = conn.execute(f"PRAGMA table_info({source_table})").fetchall()
    master_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (source_table,),
    ).fetchone()
    source_sql = master_row[0] if master_row else ""

    has_autoincrement = bool(re.search(
        r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
        source_sql,
        re.IGNORECASE,
    ))
    id_decl = "id INTEGER PRIMARY KEY AUTOINCREMENT" if has_autoincrement else "id INTEGER PRIMARY KEY"

    non_pk_rows = [row for row in pragma_rows if row[5] == 0]
    non_pk_cols = []
    non_pk_decls = []
    for cid, name, type_, notnull, dflt, pk in non_pk_rows:
        dst_name = rename_map.get(name, name)
        decl = f"{dst_name} {type_}"
        if notnull:
            decl += " NOT NULL"
        if dflt is not None:
            decl += f" DEFAULT {dflt}"
        non_pk_decls.append(decl)
        non_pk_cols.append((name, dst_name))

    addition_decls = [decl for decl, _ in additions]
    addition_selects = [select for _, select in additions]
    addition_names = [decl.split()[0] for decl in addition_decls]

    new_table = f"{source_table}_new"
    create_sql = (
        f"CREATE TABLE {new_table} ("
        + ", ".join([id_decl, *non_pk_decls, *addition_decls, constraint_clause])
        + ")"
    )

    dst_cols_in_order = ["id", *(dst for _, dst in non_pk_cols), *addition_names]
    src_exprs_in_order = ["id", *(src for src, _ in non_pk_cols), *addition_selects]

    index_snapshots = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
        (source_table,),
    ).fetchall()

    conn.execute(create_sql)
    conn.execute(
        f"INSERT INTO {new_table} ({', '.join(dst_cols_in_order)}) "
        f"SELECT {', '.join(src_exprs_in_order)} FROM {source_table}"
    )
    conn.execute(f"DROP TABLE {source_table}")
    conn.execute(f"ALTER TABLE {new_table} RENAME TO {source_table}")

    for (index_sql,) in index_snapshots:
        conn.execute(index_sql)

    conn.commit()
```

### `_migrate_job_description_versions_to_job_versions` (line 152-179) → EXTEND

Inside the existing helper, after the `ALTER TABLE job_description_versions RENAME TO job_versions` block, add (must-have #9):

```python
conn.execute("DROP INDEX IF EXISTS idx_job_description_versions_jd_id")
conn.execute("CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id)")
```

Existing rename branch keeps the same gating + side effects.

### NEW helper `_migrate_personal_info_to_users` (extracted from inline block at lines 478-494)

Source-tolerant via PRAGMA introspection (must-have #10):

```python
def _migrate_personal_info_to_users(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='personal_info'"
    )
    if cursor.fetchone() is None:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE id = 1")
    if cursor.fetchone()[0] != 0:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM personal_info WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        return
    target_columns = ("email", "full_name", "phone", "location", "linkedin_url",
                      "summary", "photo", "updated_at")
    source_columns = {row[1] for row in conn.execute("PRAGMA table_info(personal_info)").fetchall()}
    cols_present = [c for c in target_columns if c in source_columns]
    col_list = ", ".join(cols_present)
    conn.execute(
        f"INSERT INTO users (id, {col_list}) SELECT 1, {col_list} FROM personal_info WHERE id = 1"
    )
    conn.commit()
```

### NEW module-level `MIGRATIONS` (list of tuples)

Replaces current `migrations: list[str]` block (lines 381-409). After the BLOCKER 2 reconciliation, all SQL targets current names (`jobs` not `job_descriptions`); the photo entry on personal_info is removed entirely (column lives in inline DDL for users, data migration handled by `_migrate_personal_info_to_users`):

```python
MIGRATIONS: list[tuple[str, str]] = [
    ("20240601_jobs_title",                "ALTER TABLE jobs ADD COLUMN title TEXT DEFAULT 'Untitled Job'"),
    ("20240601_jobs_company_name",         "ALTER TABLE jobs ADD COLUMN company_name TEXT"),
    ("20240601_jobs_updated_at",           "ALTER TABLE jobs ADD COLUMN updated_at TEXT"),
    ("20240601_jobs_is_saved",             "ALTER TABLE jobs ADD COLUMN is_saved INTEGER DEFAULT 1"),
    ("20240601_jobs_user_id",              "ALTER TABLE jobs ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_resumes_jd_version_id",     "ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER"),
    ("20240601_resumes_language",          "ALTER TABLE generated_resumes ADD COLUMN language TEXT DEFAULT 'en'"),
    ("20240601_resumes_job_analysis",      "ALTER TABLE generated_resumes ADD COLUMN job_analysis TEXT"),
    ("20240601_resumes_user_id",           "ALTER TABLE generated_resumes ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_work_user_id",              "ALTER TABLE work_experiences ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_education_user_id",         "ALTER TABLE education ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_projects_user_id",          "ALTER TABLE projects ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20240601_languages_user_id",         "ALTER TABLE languages ADD COLUMN user_id INTEGER DEFAULT 1"),
    ("20260527_breadcrumbs_prompt_path",   "ALTER TABLE generated_resumes ADD COLUMN prompt_path TEXT"),
    ("20260527_breadcrumbs_prompt_hash",   "ALTER TABLE generated_resumes ADD COLUMN prompt_hash TEXT"),
    ("20260527_breadcrumbs_provider",      "ALTER TABLE generated_resumes ADD COLUMN provider TEXT"),
    ("20260527_breadcrumbs_model",         "ALTER TABLE generated_resumes ADD COLUMN model TEXT"),
    ("20260527_breadcrumbs_profile_snap",  "ALTER TABLE generated_resumes ADD COLUMN profile_snapshot TEXT"),
    ("20260527_breadcrumbs_raw_output",    "ALTER TABLE generated_resumes ADD COLUMN raw_output TEXT"),
    ("20260527_breadcrumbs_latency_ms",    "ALTER TABLE generated_resumes ADD COLUMN latency_ms INTEGER"),
    ("20260527_breadcrumbs_input_tokens",  "ALTER TABLE generated_resumes ADD COLUMN input_tokens INTEGER"),
    ("20260527_breadcrumbs_output_tokens", "ALTER TABLE generated_resumes ADD COLUMN output_tokens INTEGER"),
]
```

22 entries (down from 23: photo entry deleted).

### NEW `_apply_migrations(conn)` (added before `init_db`)

```python
_ADD_COLUMN_RE = re.compile(
    r"^\s*ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)\b",
    re.IGNORECASE,
)

def _apply_migrations(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_versions ("
        "version TEXT PRIMARY KEY, "
        "applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {row[0] for row in conn.execute(
        "SELECT version FROM schema_versions"
    ).fetchall()}
    for version_id, sql in MIGRATIONS:
        if version_id in applied:
            continue
        match = _ADD_COLUMN_RE.match(sql)
        if match:
            table, column = match.group(1), match.group(2)
            existing = {row[1] for row in conn.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()}
            if column in existing:
                conn.execute(
                    "INSERT INTO schema_versions (version) VALUES (?)",
                    (version_id,),
                )
                conn.commit()
                continue
        try:
            conn.execute(sql)
        except Exception as e:
            raise type(e)(f"[{version_id}] {e}") from e
        conn.execute(
            "INSERT INTO schema_versions (version) VALUES (?)",
            (version_id,),
        )
        conn.commit()
```

### `init_db()` (lines 268-501) → REORDER + SIMPLIFY

The new body follows the 8-step execution order from FEATURE_SPEC v5:

```python
def init_db():
    with get_db() as conn:
        conn.executescript(_INLINE_DDL)              # step 2
        _migrate_job_descriptions_to_jobs(conn)
        _migrate_raw_text_to_original_text(conn)
        _migrate_job_description_versions_to_job_versions(conn)   # extended (#9)
        _migrate_personal_info_to_users(conn)         # new (#10)
        _migrate_skills_unique_constraint(conn)       # refactored (#3)
        _migrate_generated_resumes_fk_cascade(conn)   # refactored (#3)
        _apply_migrations(conn)                       # steps 4-5
        # step 6 — backfills, idempotent
        conn.execute(
            "UPDATE jobs SET updated_at = created_at WHERE updated_at IS NULL"
        )
        conn.execute(
            "UPDATE generated_resumes "
            "SET job_analysis = (SELECT parsed_data FROM jobs WHERE jobs.id = generated_resumes.job_id) "
            "WHERE job_analysis IS NULL"
        )
        conn.execute("DROP TABLE IF EXISTS personal_info")  # step 7
        conn.commit()
```

The inline DDL becomes a module-level string `_INLINE_DDL` to keep the function compact and grep-able.

### Imports at top of `database.py`

Add `import re` for the `_ADD_COLUMN_RE` pattern + AUTOINCREMENT regex. Other imports stay.

## Test file plan — `tests/test_database_migrations.py`

Keep the existing 3 tests (`test_fresh_install_includes_breadcrumb_columns`, `test_init_db_idempotent_with_breadcrumb_columns`, `test_recreate_path_preserves_breadcrumb_columns`).

Add 9 new tests, one per scenario:

1. `test_fresh_install_skips_recreates_and_seeds_versions` — monkeypatched call-counting wrappers on the two recreate helpers; assert each wrapper invoked but no `*_new` table created during invocation (use `set_trace_callback` per-call); assert `sqlite_master.sql` for `generated_resumes` contains `ON DELETE CASCADE`; assert `skills.sql` contains `UNIQUE(user_id, name)`; assert `schema_versions` row count equals `len(database.MIGRATIONS)`.

2. `test_upgrade_path_matches_fresh_install` — build a "legacy 2024 snapshot" DB (writes specific minimal CREATE TABLE statements + seed rows), call `init_db()`, build a fresh-install DB in a second tempfile, run a `pragma_equivalent(db_a, db_b) -> bool` helper that compares all PRAGMA outputs across all tables.

3. `test_init_db_idempotent` — run `init_db()` twice on the same DB, capture trace strings around the second call, assert no `ALTER TABLE` / `CREATE TABLE *_new` in the trace, assert `schema_versions` row count unchanged, assert PRAGMA equivalence to self pre/post.

4. `test_recreate_preserves_extra_columns` — directly construct a `generated_resumes` table with an extra `experimental_field TEXT DEFAULT 'preserved'` column and the necessary `jobs` table; `sqlite_master.sql` lacks CASCADE so the helper's guard fails and it proceeds; call helper; assert `experimental_field` survives + row value preserved.

5. `test_failing_migration_fails_loud` — monkeypatch `MIGRATIONS` to add `("20999999_broken", "ALTER TABLE doesnotexist ADD COLUMN x TEXT")`; run `init_db()`; catch the raised `OperationalError`; format via `traceback.format_exception(type(exc), exc, exc.__traceback__)`; assert `"20999999_broken"` in the rendered string; assert no `schema_versions` row with that version_id.

6. `test_seeds_schema_versions_for_upgraded_db` — fresh DB → `init_db()` → `DROP TABLE schema_versions` → snapshot PRAGMA → second `init_db()` → assert: schema_versions exists again, rows == len(MIGRATIONS), no `ALTER TABLE` / `CREATE TABLE *_new` in trace, PRAGMA equivalence pre/post.

7. `test_dead_tables_absent_after_init` — fresh `init_db()`; assert `personal_info`, `job_descriptions`, `job_description_versions` not in `sqlite_master`.

8. `test_personal_info_data_migrates_to_users` — seed personal_info with row 1 (with photo); empty users; `init_db()`; assert users row 1 matches; assert personal_info absent.

9. `test_personal_info_helper_tolerates_missing_photo` — seed pre-photo `personal_info` (no photo column); empty users; `init_db()`; assert users row 1 has full_name/email/etc; assert `users.photo IS NULL`; assert no exceptions.

### Test helper utilities (inside the test file, at top)

- `_pragma_equivalent(db_a_path, db_b_path) -> bool` — compares schemas
  by **name-keyed equality, ignoring `cid` ordering**. Specifically:
  - Same set of table names from `sqlite_master`.
  - For each table: same set of `(name, type, notnull, dflt_value, pk)`
    tuples from `PRAGMA table_info` (compare as sets, cid is stripped).
  - For each table: same set of `(name, unique)` tuples from
    `PRAGMA index_list` filtered to `origin='c'` (explicit indexes
    only).
  - For each explicit index: same set of `(name,)` tuples from
    `PRAGMA index_info` (column membership, position-agnostic via set).
  - For each table: same set of `(from, to_table, to_col, on_delete)`
    tuples from `PRAGMA foreign_key_list`.
  Returns True iff all sets match across both DBs.

- `_count_calls(monkeypatch, module, attr) -> tuple[wrapper_fn, counter_dict]` — wraps `getattr(module, attr)` and increments a counter on each call.

- `_capture_trace(conn) -> list[str]` — context manager that attaches a
  `set_trace_callback` (positional arg) and collects captured statements;
  unsets via `conn.set_trace_callback(None)` on exit.

- `_seed_legacy_2024(db_path)` — writes the **Q1-2024 schema** as raw
  CREATE TABLE statements plus a few seed rows. The exact schema:

  ```sql
  CREATE TABLE personal_info (
      id INTEGER PRIMARY KEY DEFAULT 1,
      full_name TEXT NOT NULL, email TEXT NOT NULL,
      phone TEXT, location TEXT, linkedin_url TEXT, summary TEXT,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      CHECK (id = 1)
  );
  CREATE TABLE work_experiences (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      company TEXT NOT NULL, title TEXT NOT NULL,
      start_date TEXT NOT NULL, end_date TEXT,
      is_current INTEGER DEFAULT 0, description TEXT, location TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE education (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      institution TEXT NOT NULL, degree TEXT NOT NULL,
      field_of_study TEXT, graduation_year INTEGER, gpa REAL, notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE skills (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE
  );
  CREATE TABLE projects (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL, description TEXT, technologies TEXT, url TEXT,
      start_date TEXT, end_date TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE languages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      level TEXT NOT NULL CHECK(level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
      display_order INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE job_descriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      raw_text TEXT NOT NULL, parsed_data TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE generated_resumes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      job_description_id INTEGER NOT NULL,
      job_title TEXT, company_name TEXT, match_score REAL,
      resume_content TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id)
  );
  CREATE INDEX idx_generated_resumes_created ON generated_resumes(created_at DESC);
  ```

  Notes on this snapshot:
  - No `users` table (pre-user-domain redesign).
  - No `job_versions` / `job_description_versions` table (also added
    later). The migration helper for that doesn't fire because the
    legacy table doesn't exist; `init_db()`'s inline DDL creates
    `job_versions` directly.
  - `skills` has `UNIQUE(name)` only (legacy constraint).
  - `generated_resumes` has the original 8 columns, no breadcrumbs,
    no language/job_analysis/user_id/jd_version_id, FK without CASCADE.

  Seed rows: insert one `personal_info` row (id=1), one
  `job_descriptions` row, one `generated_resumes` row referencing the
  job. Other tables seeded empty (sufficient for column-survival
  assertions).

## Risks (carried from FEATURE_SPEC + plan-level additions)

| # | Plan-level risk | Mitigation |
|---|---|---|
| P1 | Index snapshot SQL stored on `idx_generated_resumes_created` references the table by its name `generated_resumes`. After DROP+RENAME, the SQL is replayed verbatim. Does that re-attach the index to the new (renamed) table correctly? | Yes — the saved SQL references the table by name. After DROP+RENAME, the new table has the same name. Re-executing the SQL creates the index on the (correct) named table. Verified by reading the snapshot's content for `idx_generated_resumes_created`: `CREATE INDEX IF NOT EXISTS idx_generated_resumes_created ON generated_resumes(created_at DESC)`. |
| P2 | Single-line `INSERT` over multi-row table is wrapped in a single statement; if it has a syntax error (constructed SQL), the destination is left as a half-populated table. | The new helper does CREATE + INSERT + DROP + RENAME in order; if INSERT fails, DROP+RENAME never fire, the source data is preserved. The constructed SQL is built from PRAGMA + literals, no user input. Risk is constrained. |
| P3 | The "20240601_..." version IDs are not the real historical commit dates; pulling from git history would be more accurate but the spec says "best-effort historical" is acceptable since the runner uses set membership. | Acceptable per spec. The version_id is for human-readability, not ordering. |
| P4 | The `_apply_migrations` exception-wrapping pattern `raise type(e)(f"[{version_id}] {e}") from e` constructs the new exception with a single-string arg, which works for `OperationalError`. Other exception types might have different constructors. | All current MIGRATIONS entries are ALTER TABLE — only `OperationalError` is in play. If a future entry uses different SQL that could raise a different exception type, the pattern still works for any exception whose constructor accepts a single string. Documented as a known constraint in a code comment-free docstring (per lean-code, no inline comments; the limitation is captured in the file header). |
| P5 | `_pragma_equivalent` test helper compares row-by-row across PRAGMA outputs. Row ordering from `PRAGMA index_list` may not be deterministic across DBs. | Sort by name before comparison in the helper. Documented in the helper's two-line docstring. |
| P6 | `tests/conftest.py`'s `setup_test_db` fixture runs `init_db()` on every test. If any of the 30+ existing tests assumes inline-DDL-only behavior (pre-CASCADE generated_resumes), the refactor could surface a hidden coupling. | Run the full suite as the regression net (`test-runner` dispatch later). Existing 3 tests in `test_database_migrations.py` already exercise breadcrumb columns post-recreate, so the CASCADE path is hot. Any breakage surfaces in test-runner; no separate prep needed. |

## Lean-code rules applied to new code

The file `database.py` already uses non-conforming names (`get_or_404`, `_migrate_*`). The "public surface unchanged" must-have forbids renaming existing symbols. New symbols added:

- `MIGRATIONS` — UPPER_CASE module constant, no verb needed.
- `_apply_migrations` — `apply` not in the lean-code verb list but matches file convention. Alternative: `_update_schema_versions`. Picking `_apply_migrations` for clarity ("apply" is unambiguous in migration context); document the verb choice in the file header rationale comment.
- `_recreate_table_with_constraint` — `recreate` not in lean-code list; matches the `_migrate_*` family's compound-verb pattern.
- `_migrate_personal_info_to_users` — matches existing `_migrate_*` family.
- `_ADD_COLUMN_RE` — regex constant, UPPER_CASE convention.
- `_INLINE_DDL` — string constant.

File header (two lines) goes at the top of `database.py` per CLAUDE.md:

```python
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: SQLite engine, session context manager, and schema migration runner.
```

No other comments anywhere in the body (lean-code rule).

For `tests/test_database_migrations.py`, the existing file has a multi-line docstring at the top. Replace with a two-line header per lean-code (or extend with a brief scope sentence). The existing test functions have non-conforming names (`test_fresh_install_includes_breadcrumb_columns`) — keep them (test names are not refactor scope). New tests follow the same `test_*` pytest convention.

## Test plan summary

After this refactor:

- `tests/test_database_migrations.py`: 12 tests (3 existing + 9 new)
- All other `tests/test_*.py`: unchanged, exercise `init_db()` via `setup_test_db` fixture
- Regression net is automatic via existing 30+ test files

## Verification path for the build phase

1. Read CHECKLIST (next subagent dispatch).
2. Edit `database.py` symbol-by-symbol per the symbols-to-touch list above.
3. Edit `tests/test_database_migrations.py` — write helpers first, then 9 tests.
4. Run `uv run pytest tests/test_database_migrations.py -v` first (focused suite).
5. Run `uv run pytest` full suite for regression check.
6. Boot the dev server and confirm `init_db()` runs without raising (manual smoke).
