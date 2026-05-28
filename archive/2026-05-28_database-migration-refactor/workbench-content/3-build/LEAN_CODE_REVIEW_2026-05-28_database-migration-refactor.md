# Lean Code Review — database-migration-refactor

- feature: database-migration-refactor
- date: 2026-05-28
- status: ISSUES
- reviewer: lean-code-reviewer
- diff_base: HEAD
- files_reviewed: 2
- tolerance_note: Pre-existing legacy names (`get_or_404`, `exists_or_404`, `fetch_one`, `get_db`, `init_db`, `_migrate_*` family) are exempted per FEATURE_SPEC must-have #8 ("public surface unchanged"). The new symbol `_migrate_personal_info_to_users` joins that legacy family by design and is therefore tolerated on the verb axis only.

## Scope of adversarial focus

NEW symbols audited (in addition to the legacy-tolerance pass):

- `database.py`: `_INLINE_DDL`, `MIGRATIONS`, `_ADD_COLUMN_RE`, `_recreate_table_with_constraint`, `_migrate_personal_info_to_users`, `_apply_migrations`
- `tests/test_database_migrations.py`: full file is new content; all module-level helpers audited.

---

## 1. Verb violations (function-name verb check)

| file:line | declared_name | forbidden_verb | suggested_verb | severity |
|-----------|---------------|----------------|----------------|----------|
| database.py:212 | `_recreate_table_with_constraint` | `recreate` | `create` (already had a `_drop_*` path; the function fundamentally writes a new table → `_create_table_with_constraint` or `_write_table_with_constraint`) | MAJOR |
| database.py:404 | `_apply_migrations` | `apply` | `update` (the function updates the database schema). Alternatively `_write_migrations`. | MAJOR |
| tests/test_database_migrations.py:97 | `_capture_trace` | `capture` | `read` (`_read_trace` — yields trace lines via context manager) | MAJOR |
| tests/test_database_migrations.py:106 | `_count_calls` | `count` | `check` (the helper instruments a function so callers can `check` call count; or rename to `_create_call_counter`). | MAJOR |

Tolerated under FEATURE_SPEC #8:

- `_migrate_personal_info_to_users` — verb `migrate` is not in the permitted list, but it joins the existing `_migrate_*` family by spec.

---

## 2. Scope-size violations (verb + max 3 words)

| file:line | name | words_after_verb |
|-----------|------|------------------|
| database.py:212 | `_recreate_table_with_constraint` | 3 (table, with, constraint) — at the limit; "with" is filler. Suggest `_create_table_constrained`. | MINOR |
| database.py:358 | `_migrate_personal_info_to_users` | 4 (personal, info, to, users) — exceeds the limit. Tolerated under legacy family. | TOLERATED |
| database.py:331 | `_migrate_job_description_versions_to_job_versions` (pre-existing) | 7 — egregious but legacy. | TOLERATED |

Net new scope violations: 0 MAJOR (one MINOR at the boundary on `_recreate_table_with_constraint`).

---

## 3. God-function findings

| file:line | name | lines | jobs_detected |
|-----------|------|-------|---------------|
| database.py:212 | `_recreate_table_with_constraint` | ~59 (212–270) | 4 distinct jobs in one body: (a) read source pragma + master SQL, (b) parse columns into destination decls/pairs, (c) snapshot indexes, (d) write new table + copy rows + drop + rename + replay indexes. The function is the riskiest single block of the refactor — it both interprets the source schema and mutates it. | MAJOR |
| database.py:404 | `_apply_migrations` | ~35 (404–437) | 3 jobs: read applied set, parse ADD-COLUMN regex + skip-if-present check, execute SQL + write version row. The skip-if-already-applied branch is functionally a second concern (back-fill seeding) wedged into the main loop. | MINOR |

`_recreate_table_with_constraint` would split cleanly into:
- `_read_source_table_shape(conn, source_table)` → returns id_decl, non_pk_pairs, non_pk_decls, index_snapshots
- `_create_replacement_table(conn, source_table, shape, rename_map, additions, constraint_clause)` → writes new table + copies rows
- `_update_table_swap(conn, source_table)` → drop/rename
- `_create_table_indexes(conn, index_snapshots)` → replay indexes

The current single-function form violates rule 6 ("one function, one job") squarely. This is the headline finding.

---

## 4. Framework-suffix findings

| file_or_class | suffix | suggested_name |
|---------------|--------|----------------|
| _none_ | — | — |

NEW symbols are free of `Service`/`Manager`/`Helper`/`Utils`/`Handler`/`DTO`/`Entity`/`Model`/`Factory`/`Builder`/`Provider`/`Adapter`. The constant suffix `_RE` on `_ADD_COLUMN_RE` is a regex-module convention and not a framework jargon flag — passing.

---

## 5. Comment violations

| file | non-header_comment_count | sample_lines |
|------|--------------------------|--------------|
| database.py | 0 | clean — header lines 1–2 only, zero inline comments / docstrings across 460 lines | PASS |
| tests/test_database_migrations.py | 0 | clean — header lines 1–2 only, zero inline comments / docstrings across 567 lines | PASS |

The implementer held the line on comments. Genuinely clean — no docstrings, no inline rationale notes, no JSDoc-style trailing comments. Names carry the load.

---

## 6. Abbreviation findings (additional rule 3 sweep)

| file:line | identifier | abbreviation_of | severity |
|-----------|------------|------------------|----------|
| database.py:227 | `non_pk_rows`, `non_pk_pairs`, `non_pk_decls` | `pk` → `primary_key`; `decls` → `declarations` | MAJOR |
| database.py:230 | `_pk` (unpacked tuple element) | `pk` → `primary_key` | MINOR (unused) |
| database.py:230 | `dflt` (pragma row default) | `dflt` → `default_value` | MINOR (mirrors pragma column) |
| database.py:225 | `id_decl` | `decl` → `declaration` | MAJOR |
| database.py:232 | `decl` (loop var) | `decl` → `declaration` | MAJOR |
| database.py:232 | `dst_name` | `dst` → `destination` | MAJOR |
| database.py:240–242 | `addition_decls`, `addition_selects`, `addition_names` | `decls` → `declarations` | MAJOR |
| database.py:251 | `dst_cols_in_order` | `dst` → `destination`; `cols` → `columns` | MAJOR |
| database.py:252 | `src_exprs_in_order` | `src` → `source`; `exprs` → `expressions` | MAJOR |
| database.py:241 | `addition_selects` (re-use of `select` as a noun is fine) | — | OK |
| tests/test_database_migrations.py:64–93 | `conn_a`, `conn_b`, `tables_a`, `tables_b`, `cols_a`, `cols_b`, `idx_a`, `idx_b`, `cols_idx_a`, `cols_idx_b`, `fks_a`, `fks_b` | `cols` → `columns`; `idx` → `index`; `fks` → `foreign_keys` | MAJOR |
| tests/test_database_migrations.py:106 | `attr_name` parameter | `attr` → `attribute` | MAJOR |
| tests/test_database_migrations.py:284–285 | `skills_counter`, `gr_counter` | `gr` → `generated_resumes` (project-local abbreviation) | MAJOR |
| tests/test_database_migrations.py:294 | `gr_sql` | `gr` → `generated_resumes` | MAJOR |

The abbreviation count on `_recreate_table_with_constraint` is the secondary headline: the local namespace inside that function alone has six abbreviations (`pk`, `decl`, `dst`, `src`, `cols`, `exprs`). A future reader will translate each one in their head — exactly what rule 3 forbids. Rename the body's locals to `non_primary_key_rows`, `column_declaration`, `destination_name`, `source_expressions`, etc.

---

## Almost flagged (3 weakest spots that were tolerated)

1. **`_recreate_table_with_constraint` parameter `constraint_clause`** — `clause` is borderline jargon (SQL-specific), but it's a domain term that doesn't shorten anything. Tolerated.
2. **`init_db` orchestrator** — 20 lines calling 7 migration steps. Could be argued as a god function (read DDL → call N migrators → patch jobs.updated_at → patch generated_resumes.job_analysis → drop personal_info). I let it pass because each step is one named call and the data-back-fill SQLs are exactly the kind of one-off statements the function exists to orchestrate. Borderline.
3. **`_apply_migrations`'s try/except wrapping the executed SQL with `[{version_id}] {e}`** — this is functionally a render step (annotating the exception). Could be extracted to `_render_migration_error(version_id, error)`. Letting it pass because it's three lines and inline raise-from is idiomatic.

---

## Final verdict

**ISSUES**

Two MAJOR axes:

1. **Verb violations** — 4 new functions use forbidden verbs (`_recreate_*`, `_apply_*`, `_capture_*`, `_count_*`). Rule 1 is unconditional; "recreate" and "apply" are not in the nine permitted verbs no matter how natural they feel for a migration runner.
2. **God function + abbreviation density** — `_recreate_table_with_constraint` does four jobs in one body (rule 6) and packs six abbreviations into its local namespace (rule 3). It is the single biggest readability liability introduced by this refactor.

Plus one tolerated-with-noted-pressure point: `_migrate_personal_info_to_users` joining the legacy `_migrate_*` family is fine *for this refactor* but should be revisited when the public-surface freeze lifts.

Counts:

- verb_violations: 4 (all NEW; legacy `_migrate_*` and `get_*`/`fetch_*` excluded by spec)
- scope_violations: 0 MAJOR (1 MINOR at the limit)
- god_functions: 1 MAJOR + 1 MINOR
- framework_suffixes: 0
- comment_violations: 0
- abbreviation_violations: 9 MAJOR clusters across both files

Recommend the implementer rename:
- `_recreate_table_with_constraint` → `_create_table_constrained` (and split body)
- `_apply_migrations` → `_update_schema_versions` or `_write_pending_migrations`
- `_capture_trace` → `_read_sql_trace`
- `_count_calls` → `_create_call_counter`

And scrub `pk`/`decl`/`dst`/`src`/`cols`/`exprs`/`idx`/`fks`/`gr` from the bodies and test locals.
