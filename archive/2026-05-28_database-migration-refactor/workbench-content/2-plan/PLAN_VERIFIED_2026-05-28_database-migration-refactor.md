# PLAN_VERIFIED — database-migration-refactor

```
feature: database-migration-refactor
date: 2026-05-28
status: ISSUES
reviewer: plan-reviewer
inputs_reviewed:
  - workbench/1-analyze/spec/FEATURE_SPEC_2026-05-28_database-migration-refactor.md
  - workbench/2-plan/design/IMPL_PLAN_2026-05-28_database-migration-refactor.md
  - workbench/2-plan/design/CHECKLIST_2026-05-28_database-migration-refactor.md
  - workbench/2-plan/library_notes/SQLITE_NOTES_2026-05-28.md
  - database.py (read-only)
  - tests/test_database_migrations.py (read-only)
```

---

## 1. Traceability table

| Must-have | Covered by | Status |
|---|---|---|
| #1 Inline DDL produces post-refactor target shape | IMPL_PLAN "Inline DDL block … → REWRITE" + new `skills`/`generated_resumes` shapes shown | covered |
| #2 Drop dead inline DDL | IMPL_PLAN "Remove these `CREATE TABLE IF NOT EXISTS` blocks entirely" | covered |
| #3 Recreate helpers use dynamic CREATE from PRAGMA + constraint + additions + index snapshots | IMPL_PLAN `_recreate_table_with_constraint` pseudocode block + per-helper call-site refactors | covered |
| #4 `schema_versions` table | IMPL_PLAN `_apply_migrations` body opens with `CREATE TABLE IF NOT EXISTS schema_versions ...` | covered |
| #5 MIGRATIONS list shape change | IMPL_PLAN "NEW module-level `MIGRATIONS`" block (22 entries) | covered |
| #6 Fail-loud semantics | IMPL_PLAN `_apply_migrations` body's `raise type(e)(f"[{version_id}] {e}") from e` | covered |
| #7 Seeding via mechanical predicate | IMPL_PLAN `_apply_migrations` body's match → INSERT-without-running branch | covered |
| #8 Public surface unchanged | IMPL_PLAN "Files to touch" + "Existing public helpers (keep, signatures unchanged)" | covered |
| #9 Extend job_description_versions helper to fix index name | IMPL_PLAN "`_migrate_job_description_versions_to_job_versions` → EXTEND" | covered |
| #10 Extract `_migrate_personal_info_to_users` with source-column tolerance | IMPL_PLAN "NEW helper `_migrate_personal_info_to_users`" with PRAGMA introspection | covered |

All 10 must-haves are claimed-covered. However, two of those coverages contain construction bugs in their pseudocode (see findings B1 and B2).

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `/Users/aissacasa/.../MyCV-2/database.py` | modify | yes | ok |
| `/Users/aissacasa/.../MyCV-2/tests/test_database_migrations.py` | modify | yes | ok |
| `database.py:55-91` `_migrate_skills_unique_constraint` | modify (refactor) | yes (line 55) | ok |
| `database.py:152-179` `_migrate_job_description_versions_to_job_versions` | modify (extend) | yes (line 152) | ok |
| `database.py:182-265` `_migrate_generated_resumes_fk_cascade` | modify (refactor) | yes (line 182) | ok |
| `database.py:268-501` `init_db()` | modify (reorder) | yes (line 268) | ok |
| `database.py:270-377` inline DDL block | modify (rewrite) | yes (executescript block at 270-377) | ok |
| `database.py:381-409` `migrations` list | replace with `MIGRATIONS` | yes (381-409) | ok |
| `database.py:411-414` swallowed-exception block | remove | yes (411-414 try/except OperationalError pass) | ok |
| `database.py:422-455` `job_versions` CREATE | move into inline DDL | yes; note plan also says "(line 444-455)" — same block, slightly different anchor, both valid | ok |
| `database.py:423-434` `job_description_versions` CREATE | remove entirely | yes (423-434) | ok |
| `database.py:438` `_migrate_job_descriptions_to_jobs` call | keep, reorder | yes | ok |
| `database.py:478-494` inline `personal_info → users` block | extract to helper | yes; the IF starts at 483 (the table-exists check at 478 is part of the same logical block) | ok |
| `database.py:500` `DROP TABLE IF EXISTS personal_info` | reposition | yes (line 500) | ok |
| `tests/test_database_migrations.py` 3 existing tests | keep | yes (lines 27, 44, 63) | ok |

No hallucinated files. No hallucinated symbols.

---

## 3. Library-pattern verification

| Pattern | Documented in SQLITE_NOTES | Status |
|---|---|---|
| `PRAGMA table_info` tuple shape `(cid, name, type, notnull, dflt_value, pk)` | §1 | ok |
| `PRAGMA foreign_key_list` tuple shape with `on_delete` | §2 | ok |
| `PRAGMA index_list` with `origin='c'` filter | §3 | ok |
| `sqlite_master WHERE type='index' AND sql IS NOT NULL` filter | §4 | ok |
| `set_trace_callback` positional-only requirement | §5 | ok |
| AUTOINCREMENT case-insensitive regex against `sqlite_master.sql` | §6 | ok |
| `raise type(e)(f"[ctx] {e}") from e` chaining preserves subclass | §7 | ok |
| `sqlite3.version` / `version_info` deprecation avoidance | "Deprecated to avoid" | ok |

Library patterns are well-cited. Note `sqlite_master.sql` casing preservation note in IMPL_PLAN's first bullet under "Library patterns" reads `re.IGNORECASE` (line 25), aligned with SQLITE_NOTES §6 — consistent.

---

## 4. Checklist coverage

| Plan file/symbol | CHECKLIST items | Status |
|---|---|---|
| `database.py` inline DDL rewrite | (no direct verifiable item asserting inline DDL changes — only indirect via scenarios 1, 2, 7) | partial — see M1 |
| `_recreate_table_with_constraint` (new) | Section 2 items on PRAGMA table_info row indexing + sqlite_master `sql IS NOT NULL` + AUTOINCREMENT regex | ok |
| `_migrate_skills_unique_constraint` refactor | covered indirectly via scenario 1 (`UNIQUE(user_id, name)` present) + scenario 2 (PRAGMA equivalence) | partial |
| `_migrate_generated_resumes_fk_cascade` refactor | scenario 1 + scenario 4 | ok |
| `_migrate_job_description_versions_to_job_versions` extension (DROP+CREATE INDEX) | (no direct item asserting `idx_job_versions_job_id` is created or `idx_job_description_versions_jd_id` is dropped) | gap — see M2 |
| `_migrate_personal_info_to_users` extraction | scenario 8 + scenario 9 | ok |
| `MIGRATIONS` (new) list | indirectly via scenario 1 row count assertion | partial |
| `_apply_migrations` | scenario 5 (fail-loud), scenario 6 (seeds for upgraded DB) | ok |
| `init_db()` reorder | (no checklist item walks the exact 8-step order) | partial — see M3 |
| Removed swallow `try/except sqlite3.OperationalError: pass` | (no checklist item explicitly asserts the swallow block is gone) | gap — see M4 |
| `personal_info` table-exists guard in helper (line 200 in pseudocode) | (no checklist item asserts the helper no-ops when `personal_info` table is absent — the fresh-install path) | gap |

Several gaps but all mitigated by scenario-level assertions. No orphans (every CHECKLIST item traces to plan or library notes).

---

## 5. Risks and ambiguities — findings

### BLOCKER B1 — `_recreate_table_with_constraint` will reject `INSERT INTO generated_resumes_new` on a legacy DB because source schema is missing breadcrumb columns

**Location:** IMPL_PLAN lines 119-178 (`_recreate_table_with_constraint` pseudocode) combined with the execution order at lines 300-321 (`init_db` body).

**Trace through Scenario 2 (legacy 2024 DB):**

The legacy `generated_resumes` schema (per the existing test `test_recreate_path_preserves_breadcrumb_columns` at lines 79-93 and per `_seed_legacy_2024`'s intended shape) contains only:
`id, job_description_id, job_title, company_name, match_score, resume_content, created_at, updated_at`.

The post-refactor execution order calls `_migrate_generated_resumes_fk_cascade(conn)` BEFORE `_apply_migrations(conn)` (IMPL_PLAN line 309 then 310). At the point the recreate helper fires:

- `PRAGMA table_info(generated_resumes)` returns 8 rows (the legacy 8 columns).
- `_recreate_table_with_constraint` builds the destination as: `id INTEGER PRIMARY KEY [AUTOINCREMENT]` + 7 non-pk source columns (with `job_description_id → job_id` via rename_map) + constraint.
- The new table will have **only 8 columns total** (id + 7 mapped non-pk + 0 additions).
- After DROP+RENAME, `generated_resumes` is missing `jd_version_id`, `language`, `job_analysis`, `user_id`, and all 9 breadcrumb columns.

Then `_apply_migrations` runs and tries to `ALTER TABLE generated_resumes ADD COLUMN jd_version_id INTEGER`, `... language`, `... job_analysis`, `... user_id`, and the 9 breadcrumb ALTERs. **Each will succeed** (because the columns are absent), and `schema_versions` will get one row per applied migration.

This looks like it works — but Scenario 2's assertion is **PRAGMA equivalence with a fresh-install DB**. On a fresh install, the inline DDL creates `generated_resumes` with all 21 columns AND the same 13 ALTER migrations target a table that already has those columns, so they early-return via the predicate (column-already-exists → INSERT into schema_versions without running SQL). Both DBs end up with the same 21 columns, the same constraints, and the same 22 rows in schema_versions.

So this is **NOT actually a blocker for Scenario 2's correctness** — the upgrade path works because MIGRATIONS fills in the missing columns AFTER the recreate prunes them. But it surfaces a **load-bearing assumption nowhere stated in the plan**: the recreate helper's "preserve any extra columns" guarantee from Scenario 4 has the *exact opposite* outcome on the legacy 2024 DB — it doesn't preserve, it strips columns the new schema requires, relying on MIGRATIONS to repopulate them afterward. The plan's natural-language description in IMPL_PLAN line 88 — "Recreate carries any extra column through" — describes Scenario 4's path; it does NOT describe what happens to the 13 missing-on-legacy columns on the 2024 path.

**Severity reasoning:** The end-state is still correct, so this isn't a logic blocker. However it is a **MAJOR documentation gap** because:

1. The plan's recreate-preserves-columns language (must-have #3, IMPL_PLAN line 88) misleads about what happens on the legacy upgrade.
2. The test `test_upgrade_path_matches_fresh_install` will pass for the wrong-feeling reason — not because the recreate carried things through, but because MIGRATIONS retroactively patched the gap.
3. A future maintainer reading the plan + helper will assume the recreate is idempotent w.r.t. column count and may add an `ALTER` migration before the recreate in the execution order, breaking everything.

**Reclassify: MAJOR (not blocker).**

### BLOCKER B2 — `_apply_migrations`'s commit-per-row vs. recreate's commit pattern breaks atomicity if exception fires mid-list

**Location:** IMPL_PLAN lines 269-294 (`_apply_migrations` body), specifically the `conn.commit()` inside the for-loop at lines 283 and 293.

The pattern is:

```
for version_id, sql in MIGRATIONS:
    if already_applied: continue
    if column_already_present:
        INSERT INTO schema_versions VALUES (version_id)
        conn.commit()              # commit #1
        continue
    try: conn.execute(sql)
    except: raise type(e)(...)
    INSERT INTO schema_versions VALUES (version_id)
    conn.commit()                  # commit #2
```

This commits after each successful migration. Two consequences:

1. If migration N+1 raises but N was committed, the DB is left in a half-applied state. The next `init_db()` retries from N+1 because `schema_versions` records N as applied. This is **correct fail-loud behavior** consistent with must-have #6. But Scenario 5's assertion is "no `schema_versions` row with version_id `"20999999_broken"`" — and the assertion holds because the broken migration's INSERT into schema_versions only happens after `conn.execute(sql)` succeeds. So this is consistent.

2. **More subtle:** the `_recreate_table_with_constraint` helper also calls `conn.commit()` at its end (IMPL_PLAN line 177). The `get_db()` context manager at `database.py:45-52` does NOT call `conn.commit()` on exit (it only closes the connection). So the plan's reliance on commits inside helpers and inside `_apply_migrations` is the only mechanism persisting changes. **This is consistent** with the existing code's pattern.

**Reclassify: not an issue.**

### MAJOR B3 — `_migrate_personal_info_to_users` helper's existence-of-`users`-table assumption

**Location:** IMPL_PLAN line 202-203.

The helper's gating at line 202 calls `SELECT COUNT(*) FROM users WHERE id = 1` immediately after the personal_info-exists check. This assumes `users` table exists. On the new execution order, the inline DDL block runs first (line 303), which creates `users`. So `users` exists by the time the helper runs. **Not an issue in practice**, but the helper is also documented (FEATURE_SPEC must-have #10) as joining "the legacy `_migrate_*` family" — i.e., callable as a standalone helper. If a test calls it directly without an inline-DDL prelude, it crashes.

**Severity: MINOR** — the plan doesn't claim direct-callability as a contract; the implementation will work in the documented execution order. Documented for future maintainers.

### MAJOR B4 — `_recreate_table_with_constraint`'s `id INTEGER PRIMARY KEY [AUTOINCREMENT]` assumes pk column is always named `id`

**Location:** IMPL_PLAN line 132: `id_decl = "id INTEGER PRIMARY KEY AUTOINCREMENT" if has_autoincrement else "id INTEGER PRIMARY KEY"`.

The pseudocode hardcodes the pk column name as `id` and the type as `INTEGER`. It does NOT derive these from the PRAGMA row where `pk=1`. If a source table had a pk column named something else (e.g., `user_id` as pk, or composite pk), the plan's code would emit a wrong DDL.

**Mitigation context:** In the current codebase, both touched tables (`skills` and `generated_resumes`) have `id INTEGER PRIMARY KEY AUTOINCREMENT`. So the hardcoding is correct for the two specific callers. But the plan presents `_recreate_table_with_constraint` as a general helper.

**Severity: MAJOR.** This is the kind of "works today, hides a bug for the next maintainer" trap the feature spec explicitly tries to prevent (per the pain point). The plan should either:
- Document that the pk column MUST be named `id` of type `INTEGER` for this helper (in the function's two-line scope header), OR
- Derive the pk declaration from `[row for row in pragma_rows if row[5] != 0]`.

Plan does neither. Add to file-header note alongside the COLLATE / generated-column limitations.

### MAJOR B5 — `idx_generated_resumes_created` is created in CURRENT inline DDL but NOT explicitly preserved by the plan's new inline DDL specification

**Location:** IMPL_PLAN lines 47-67 (Inline DDL block at `init_db()` REWRITE section).

The current `database.py:375-376` creates `CREATE INDEX IF NOT EXISTS idx_generated_resumes_created ON generated_resumes(created_at DESC);` as part of the inline DDL. The IMPL_PLAN says (line 57) `generated_resumes` (line 354-373) — change to the post-CASCADE shape with all columns from the post-history state, but it does NOT explicitly say "and preserve the `idx_generated_resumes_created` index in the inline DDL block."

**Risk:** If the implementer reads "rewrite" literally and omits the index, fresh installs lose that index. The PRAGMA-equivalence test would catch it (the legacy path snapshots and restores the index — Scenarios 2 and 6 — but fresh install would lack it, so they wouldn't be equivalent). However the implementer might not realize this until the test fails.

**Severity: MAJOR.** The plan should explicitly enumerate the indexes in the new inline DDL spec. (Plan-level finding P1 mentions the index name but in the context of snapshot/replay, not inline-DDL preservation.)

### MAJOR B6 — `_seed_legacy_2024` is underspecified

**Location:** IMPL_PLAN line 359; CHECKLIST line 57.

The plan says "writes CREATE TABLE statements + a few seed rows simulating a Q1-2024 DB shape (pre-CASCADE, pre-rename, pre-photo)." It does NOT specify:
- Which tables to create (the 2024 set: `personal_info`, `job_descriptions`, `job_description_versions`, `users`?, `work_experiences`, `education`, `skills`, `projects`, `languages`, `generated_resumes`).
- The exact column lists for each — critical because if the legacy `generated_resumes` is seeded with columns that already include some breadcrumb fields, the recreate's column-preservation behavior changes.
- Whether `skills` has UNIQUE(name) (per FEATURE_SPEC Scenario 2 "skills with UNIQUE(name) (no user_id)") — this matters because the AUTOINCREMENT regex check in `_recreate_table_with_constraint` requires the exact CREATE string.
- Which migrations from MIGRATIONS should already be present (e.g., does Q1-2024 include the `jobs.title` column? The current `database.py:382` migration was added later per spec).

The implementer will have to invent these details. Two different invented shapes produce two different test outcomes.

**Severity: MAJOR.** The PRAGMA-equivalence test's value depends entirely on `_seed_legacy_2024` producing a legacy-shaped DB whose post-upgrade state matches fresh install. Underspecification = the implementer guesses, the test passes/fails based on the guess, and the plan's "verified by Scenario 2" claim is hollow.

### MAJOR B7 — `_pragma_equivalent` row-stability question (FEATURE_SPEC R6 mitigation)

**Location:** IMPL_PLAN lines 356, 369 (P5); CHECKLIST line 54.

P5 says "Sort by name before comparison in the helper." But the rows for `PRAGMA table_info` come in column-order (`cid` field). If both DBs have the same column set BUT in different `cid` order (e.g., legacy DB has columns added by `ALTER` after the recreate, fresh install has them inline), the `cid` differs. The plan's mitigation "Sort by name" addresses index-list ordering, but NOT the cid mismatch in `table_info` outputs.

Two reads of "PRAGMA-equivalent":
1. Same set of `(name, type, notnull, dflt_value, pk)` tuples ignoring `cid` — sort-by-name produces stable comparison. ✓
2. Same `cid` order — column ordering matters. Fails on the legacy upgrade path because ALTER-added columns get later cids than inline-DDL'd ones.

The plan doesn't disambiguate. FEATURE_SPEC Scenario 2 says "for every table in `sqlite_master`, both DBs have the same row from `PRAGMA table_info(<table>)`" — "same row" reads as #2, which fails.

**Severity: MAJOR.** The implementer needs to know which interpretation. Recommended interpretation #1 (ignore cid). Plan should state this and CHECKLIST should add an item asserting cid is not compared.

### MINOR B8 — `_apply_migrations` ordering vs. `personal_info` photo column on a pre-photo legacy DB

**Location:** IMPL_PLAN MIGRATIONS list (line 224-247).

The plan removes the `ALTER TABLE personal_info ADD COLUMN photo TEXT` migration (per must-have #5). On a pre-photo legacy DB, the helper `_migrate_personal_info_to_users` handles the missing-column case per FEATURE_SPEC #10 (intersection of present columns and target column set). **OK.**

But there's a sequencing detail: in the new execution order, `_migrate_personal_info_to_users` runs before `_apply_migrations`. Inside the helper, the SELECT-from-personal_info uses `cols_present` which omits `photo` if absent. The corresponding INSERT into `users` also omits photo from both column lists. The `users` table inline DDL has `photo TEXT` already (line 291 of current database.py), so the column exists in `users` and the omitted INSERT leaves it NULL. **OK.**

But — if a legacy DB has `personal_info` WITH photo but the `personal_info ADD COLUMN photo` migration was NEVER applied (e.g., a DB created exactly after the photo column was added inline but before migrations ran), this could mismatch. **Practical risk: zero, because the photo migration was applied via inline DDL for all production DBs.**

**Severity: MINOR.**

### MINOR B9 — IMPL_PLAN lines 17, 81-87, 92-112 use the word "OK" / "would" / "should" loosely

Scanning the plan for vague terms per the prompt:

- IMPL_PLAN line 73 "becomes" — describes new state, not vague.
- IMPL_PLAN line 168 "in order" — sequence, not vague.
- IMPL_PLAN line 198 "as expected" — does NOT appear; checked.
- IMPL_PLAN line 365 "Verified by reading the snapshot's content" — concrete, not vague.
- IMPL_PLAN line 366 "Risk is constrained" — vague. **Specifically:** P2 says "The constructed SQL is built from PRAGMA + literals, no user input. Risk is constrained." This is a hand-wave. The risk in P2 is about a half-populated table on INSERT failure. The mitigation (CREATE-INSERT-DROP-RENAME ordering means failure mid-INSERT leaves source intact) is REAL and concrete. But "Risk is constrained" doesn't restate that — it just asserts it. **MINOR vague phrase.**
- IMPL_PLAN line 367 "best-effort historical" — vague but FEATURE_SPEC #5 already calls this out as an accepted constraint, so the plan inherits the language. OK.

**Severity: MINOR.**

### MINOR B10 — `_INLINE_DDL` module-level constant is named but its full content is not enumerated

**Location:** IMPL_PLAN line 324.

The plan introduces `_INLINE_DDL` as a module-level string holding the new inline DDL. It tells the implementer what shape to produce (per the per-table descriptions in lines 41-67) but does NOT enumerate the full string content. This is consistent with the plan's level-of-detail elsewhere; the implementer composes the final string from the per-table specs. **Note that the implementer must also include the `CREATE INDEX idx_generated_resumes_created` line** (see B5).

**Severity: MINOR** in isolation; **escalates to MAJOR via B5.**

### MINOR B11 — Concurrency / race-conditions

The plan does not address concurrent `init_db()` calls. The current code calls `init_db()` once at startup (app.py / main.py) so concurrency is not on the path. The plan inherits this assumption. **OK.**

### MINOR B12 — IMPL_PLAN line 367 mentions "Plan-level risk P3" referencing "git history" — this is descriptive, no action item

OK.

---

## 6. Cross-cutting consistency issues

### M1 — CHECKLIST does not assert "inline DDL has only N tables"

The CHECKLIST has no `grep -c "CREATE TABLE IF NOT EXISTS" database.py` style line item that would catch a partial rewrite (e.g., implementer forgets to remove `personal_info` from the inline block). Scenario 7 catches it by absence-in-sqlite_master, but a checklist-level grep would catch it before the test runs.

**Severity: MINOR.**

### M2 — CHECKLIST does not assert the `idx_job_versions_job_id` rename actually happens

Per must-have #9, the helper extension does `DROP INDEX IF EXISTS idx_job_description_versions_jd_id` then `CREATE INDEX IF NOT EXISTS idx_job_versions_job_id ON job_versions(job_id)`. The CHECKLIST has no item asserting this DROP-and-CREATE. Indirect coverage via Scenario 2 PRAGMA equivalence, but a direct test item ("assert `idx_job_versions_job_id` exists post-init AND `idx_job_description_versions_jd_id` is absent") would be cleaner.

**Severity: MAJOR.** This is the exact R6 mitigation that prevents Scenario 2 from spuriously failing. Worth a direct check.

### M3 — CHECKLIST does not walk the 8-step `init_db` execution order

Section 4 covers tests. Section 2 covers syntax. No section asserts the call sequence in `init_db()` matches the spec's execution order. A grep-able item like `grep -A 20 "def init_db" database.py | grep -n "_migrate\|_apply\|executescript\|DROP"` would catch reorder bugs.

**Severity: MAJOR.** The execution order is load-bearing for Scenarios 1, 2, 3, 6, 8, 9.

### M4 — CHECKLIST does not assert the legacy swallow block is removed

Must-have #6 requires removal of `try/except sqlite3.OperationalError: pass` at lines 411-414. The CHECKLIST has no grep item like `grep -c "except sqlite3.OperationalError:" database.py` returns 0. Scenario 5 covers the runtime behavior but not the source-level absence.

**Severity: MINOR.**

---

## 7. Final verdict

**ISSUES**

Counts:
- BLOCKERs: 0
- MAJORs: 6 (B4, B5, B6, B7, M2, M3)
- MINORs: 7 (B3, B8, B9, B10, B11, B12, M1, M4)

The plan is structurally sound and traces well to the spec. The pseudocode for the core helper `_recreate_table_with_constraint` is concrete and traceable. However, several gaps reduce the implementer's certainty about edge behavior and the test suite's discriminating power:

- **B4 (pk-name assumption)** — hardcoded `id` in the helper without a documented contract.
- **B5 (index in inline DDL)** — the implementer might omit `idx_generated_resumes_created` from the rewritten inline DDL.
- **B6 (`_seed_legacy_2024` underspecified)** — the implementer invents the legacy shape; Scenario 2's discriminating power depends on what they invent.
- **B7 (PRAGMA-equivalent semantics)** — `cid` vs. name-only comparison is ambiguous; will likely cause the test to fail spuriously on first run.
- **M2 + M3 (CHECKLIST gaps)** — index rename and execution order both deserve explicit checklist items because they are load-bearing.

Recommended resolution:

1. IMPL_PLAN add a sentence to `_recreate_table_with_constraint` documenting the pk-column assumption (B4).
2. IMPL_PLAN explicitly enumerate the post-rewrite `_INLINE_DDL` indexes (B5).
3. IMPL_PLAN add a concrete column list for `_seed_legacy_2024` (B6) — either as a code block or a per-table table.
4. IMPL_PLAN specify `_pragma_equivalent` ignores `cid` ordering and compares on `(name, type, notnull, dflt_value, pk)` tuple sets (B7).
5. CHECKLIST add: assert `idx_job_versions_job_id` present and `idx_job_description_versions_jd_id` absent after init (M2).
6. CHECKLIST add: assert init_db function body has helper calls in the documented order (M3).

After these are applied, the plan should be VERIFIED.

Build phase should NOT proceed until the four IMPL_PLAN updates land and the two CHECKLIST items are added.
