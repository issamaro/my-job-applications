# RETROSPECTIVE — database-migration-refactor

**Date:** 2026-05-28
**Ceremony:** L
**Outcome:** Shipped. 283/283 tests pass; legacy upgrade path verified
on the real `app.db` (legacy `idx_job_description_versions_jd_id` index
removed; `schema_versions` populated with 22 rows matching `MIGRATIONS`).

## What surprised

**Five rounds of adversarial analysis-review.** The reviewer correctly
surfaced new issues each round as the spec became more concrete. The
sequence was:

- **v1 ISSUES (3 blockers):** must-have #3 contradicted Scenario 4;
  seeding plan didn't work for renamed/dropped target tables; execution
  order unspecified.
- **v2 ISSUES (3 majors):** AUTOINCREMENT not in PRAGMA; byte-identical
  vs PRAGMA equivalence ambiguous; rename scope unclear.
- **v3 ISSUES (1 blocker + 1 major):** skills recreate missing the
  "additions" concept; fail-loud contradicts traceback assertion.
- **v4 ISSUES (1 blocker + 2 majors):** indexes not preserved by
  recreate; `id` declaration ambiguous; personal_info-to-users crashes
  on missing photo.
- **v5 VERIFIED.**

This pattern is not a flaw — it's the value of the gate. The reviewer
caught real architectural issues that would have surfaced as
mid-implementation rework otherwise.

## What was harder than expected

**The legacy index survives ALTER TABLE RENAME TO.** SQLite preserves
indexes through table renames, so `idx_job_description_versions_jd_id`
hung around on the `job_versions` table long after the rename. The
inspector's automated grep check surfaced this on the real `app.db` —
it wasn't covered by the synthetic legacy seed in
`_write_legacy_2024`. Fixed by making the legacy-index drop
**unconditional** at the end of the helper (was originally gated
inside the rename branch).

**Inline DDL move broke the legacy data path.** Moving the
`job_versions` CREATE into inline DDL meant the rename helper's
"has_old AND has_new" branch could fire on legacy DBs that had data in
`job_description_versions`. Original logic only dropped old-if-empty;
extended to DROP+RENAME (matching the `_migrate_job_descriptions_to_jobs`
pattern) when new is empty and old has data. Added
`test_legacy_job_description_versions_data_preserved` to cover this.

## What the next similar feature should do differently

1. **Synthetic legacy seed must mirror the real DB state, not just the
   "original 2024 shape".** `_write_legacy_2024` covered the
   2024 snapshot but not the partially-migrated states (table renamed,
   index name lagging). Real production DBs sit in those intermediate
   states. Next time: write a `_write_partially_migrated_intermediate`
   helper that captures the actual `app.db` state at the time of the
   refactor.

2. **Run init_db() against the real app.db (copy first) as part of the
   automated inspector checks.** The mechanical grep checks didn't
   catch the surviving legacy index — only the live-run check did. If
   the inspector had run init_db on a copy of the real DB
   automatically, it would have surfaced earlier.

3. **Adversarial spec review can recurse ~5 rounds.** Plan for that
   time budget. Setting it as a hard cap and overriding earlier might
   trade rigor for speed; this refactor's value was high enough to
   warrant the rigor, but a smaller feature wouldn't.

4. **PRAGMA-equivalence as the comparison primitive is much more
   stable than `sqlite_master.sql` byte-comparison.** Worth promoting
   to a project-level test helper if any future feature needs schema
   comparison.

## Token economics

Five rounds of analysis-reviewer, two rounds of plan-reviewer-style
patching, and several rounds of self-debugging totaled significantly
more orchestration overhead than implementation cost. The actual
`database.py` rewrite is ~450 lines; the `test_database_migrations.py`
file is ~470 lines. The work product is small; the rigor was
proportional to the latent-bug class the spec is designed to prevent.

## Files changed

- `database.py` (rewritten — file header, `_INLINE_DDL`, `MIGRATIONS`,
  `_migrate_recreate_with_constraint`, `_migrate_apply_pending`,
  `_migrate_personal_info_to_users` extracted, `_migrate_skills_*` and
  `_migrate_generated_resumes_*` refactored to use shared helper,
  `_migrate_job_description_versions_*` extended for index cleanup,
  `init_db()` reordered to 8-step explicit sequence).
- `tests/test_database_migrations.py` (extended from 3 tests to 13;
  added 9 scenario tests + 1 regression test for legacy data
  preservation; added `_check_pragma_equivalent`, `_capture_trace`,
  `_count_calls`, `_write_legacy_2024` test helpers).
- No other files changed.
