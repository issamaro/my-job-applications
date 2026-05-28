# REPRO — database-migration-refactor

**Date:** 2026-05-28
**Slug:** database-migration-refactor

## Reproduction script

`/tmp/repro_migration_drift.py` — sets up a `generated_resumes` table that has
all current columns plus one extra "forgotten" column (`future_feature_column`),
then calls `_migrate_generated_resumes_fk_cascade(conn)` directly and inspects
the result.

## Actual output

```
BEFORE recreate:
  columns (22): [..., 'future_feature_column']
  has future_feature_column: True
  row value: 'this-must-survive'

AFTER recreate:
  columns (21): [..., 'output_tokens']   # future_feature_column GONE
  has future_feature_column: False
```

22 → 21 columns. The forgotten column was silently dropped. The row data in
that column (`'this-must-survive'`) is also gone — not just the schema, the
data too.

## Root cause (confirmed)

`database.py:236-251` — the recreate helper hardcodes its INSERT/SELECT column
list:

```python
INSERT INTO generated_resumes_new
(id, job_id, job_title, company_name, match_score,
 resume_content, created_at, updated_at, jd_version_id, language,
 job_analysis, user_id,
 prompt_path, prompt_hash, provider, model,
 profile_snapshot, raw_output, latency_ms,
 input_tokens, output_tokens)
SELECT id, {source_column}, job_title, company_name, match_score, ...
FROM generated_resumes
```

Any column present on the source table but absent from this hardcoded list is
silently dropped during the recreate. The recreate fires unconditionally on
fresh installs (because the inline DDL at `database.py:354-373` lacks
`ON DELETE CASCADE` so the early-return at `database.py:199` does not match).

## Why production has not seen it yet

Production DBs were created back when the inline DDL matched the table shape,
went through every migration in order, eventually got CASCADE applied via the
recreate (when it was first introduced), and now early-return on subsequent
boots. The bug only fires on **fresh installs** where the inline DDL diverges
from "post-migration target shape" and the recreate is forced to fire.

The llm-call-breadcrumbs feature dodged this because the developer who shipped
it noticed the divergence (per backlog item) and updated **both** the inline
DDL and the recreate's hardcoded column lists. But the trap remains: the next
feature to add a column to `generated_resumes` has to update the inline DDL
AND the recreate's hardcoded list, with no compile-time signal that the
recreate needs an edit. This is what the refactor eliminates.

## Smallest patch that changes the failure shape

Replacing the hardcoded INSERT/SELECT in `_migrate_generated_resumes_fk_cascade`
with a `PRAGMA table_info(generated_resumes)`-driven column copy makes the
recreate transparently carry any extra column through. Demonstrated to work
locally on the repro script — when patched, all 22 columns survive.

This patch alone fixes the immediate drift hazard. The full refactor adds:
(a) bringing inline DDL forward so the recreate's early-return fires on fresh
installs (eliminating one unnecessary recreate per fresh install), and
(b) a `schema_versions` table so migration order/idempotency are explicit
rather than implicit-via-try-except.
