# FEATURE_SPEC — llm-call-breadcrumbs

**Slug:** llm-call-breadcrumbs
**Date:** 2026-05-27 (revised after analysis-reviewer ISSUES)
**Ceremony:** M
**Shape:** backend-only (no UI)
**Persona:** Sole dev wiring up the sibling `llm-testing-framework` repo. Will consume these breadcrumbs from `/retro-prompts` (item 4 of the initiative) and from a new `llm-eval import` CLI (item 3).
**Pain:** After a generation, the parsed output is preserved on `generated_resumes.resume_content` but the *call envelope* (which prompt text was sent, which provider/model produced it, the raw pre-parse text, the exact profile dict the LLM saw) is gone. Without that, no eval framework can replay or grade historical generations — they can only re-run new ones, which defeats the point of historical analysis.

This slice fixes that **additively**: new columns, new capture path, zero behavior change for existing flows. Items 2/3/4 of the initiative depend on this landing first.

## Revisions from analysis-reviewer (2026-05-27)

The first pass of this spec hit one BLOCKER and three MAJORs. This revision
addresses all six findings inline. Side-effects: two follow-up backlog items
filed (`database-migration-refactor`, `resume-generation-atomicity`,
`ruff-ty-precommit`) so the design debt surfaced here doesn't get smuggled
into this slice.

---

## Must-have (in)

1. `generated_resumes` gains 9 new columns. The migration touches **four**
   code locations in `database.py`, not just the migrations list:

   1. **Inline DDL at `database.py:339-353`** — the `CREATE TABLE IF NOT
      EXISTS generated_resumes (...)` inside the `executescript` block
      gains the 9 new columns. (This catches fresh-install DBs before the
      legacy `_migrate_*` chain runs.)

   2. **Append 9 entries to `migrations = [...]` at `database.py:357-376`** —
      one `ALTER TABLE generated_resumes ADD COLUMN ...` per breadcrumb
      column. Each runs inside the existing try/except `OperationalError`
      idempotency wrapper. Appended at the **end** of the list so any
      database that already ran prior migrations doesn't have insertion
      order shifted underneath it.

   3. **`_migrate_generated_resumes_fk_cascade` CREATE block at
      `database.py:207-222`** — the `CREATE TABLE generated_resumes_new`
      column list inside the recreate function gains the 9 breadcrumb
      columns. Without this, fresh installs and pre-CASCADE legacy DBs
      that hit the recreate path would silently drop the columns.

   4. **`_migrate_generated_resumes_fk_cascade` INSERT/SELECT column lists
      at `database.py:228-234`** — both the INSERT target list and the
      SELECT source list gain the 9 column names. The SELECT pulls from
      the existing `generated_resumes` table (which by this point has the
      columns via the ALTER step above), so the column lists must match.

   The 9 columns:
   - `prompt_path TEXT` — sentinel `"services/llm/base.py:SYSTEM_PROMPT"` until item 2 lands
   - `prompt_hash TEXT` — hex SHA-1 of the prompt bytes actually sent
   - `provider TEXT` — `"claude"` or `"gemini"`
   - `model TEXT` — concrete model id from each provider's `_get_model()`
   - `profile_snapshot TEXT` — JSON of the photo-stripped profile dict
   - `raw_output TEXT` — unparsed LLM response text
   - `latency_ms INTEGER NULL` — measured via `time.monotonic()` deltas
   - `input_tokens INTEGER NULL` — from SDK usage if exposed, else NULL
   - `output_tokens INTEGER NULL` — from SDK usage if exposed, else NULL

   The `_migrate_generated_resumes_fk_cascade` is structurally broken
   (it requires manual edits to three column lists every time a column
   is added) and that broader fix is filed as
   `backlog/refined/database-migration-refactor.md`. This slice does the
   minimum patch to ship safely; the refactor is its own ceremony-L slice.

2. `LLMProvider` protocol in `services/llm/base.py` returns
   `tuple[dict, dict]` — `(parsed, breadcrumbs)` — from `analyze_and_generate`.
   Both providers implement the new shape. The breadcrumbs dict is owned
   by the provider, not the caller, so the provider is the single source
   of truth for "what we sent."

3. **`ClaudeProvider.analyze_and_generate` returns a breadcrumbs dict
   containing:**
   - `provider = "claude"`
   - `model = _get_model()`
   - `prompt_path = "services/llm/base.py:SYSTEM_PROMPT"`
   - `prompt_hash = hashlib.sha1((SYSTEM_PROMPT + "\n\n" + formatted_user_prompt).encode("utf-8")).hexdigest()`
   - `raw_output = response_text` (the unparsed string from `message.content[0].text`)
   - `latency_ms = int((time.monotonic() - t0) * 1000)` measured around the `client.messages.create(...)` call only (not around the JSON parse)
   - `profile_snapshot = json.dumps(profile, sort_keys=True, ensure_ascii=False)` materialized **inside the provider, before the SDK call**, using the profile dict the provider received — this is what the LLM actually sees
   - `input_tokens = getattr(message.usage, "input_tokens", None)` — accept `None` if Anthropic returns it that way; do not coerce to 0
   - `output_tokens = getattr(message.usage, "output_tokens", None)` — same NULL-not-zero rule

4. **`GeminiProvider.analyze_and_generate` returns the same breadcrumbs
   dict shape with two specifics:**
   - `provider = "gemini"`, `model = _get_model()`, `prompt_path = "services/llm/base.py:SYSTEM_PROMPT"`.
   - `prompt_hash = hashlib.sha1(full_prompt.encode("utf-8")).hexdigest()` over the actual `full_prompt` (system+user concatenated with `"\n\n"`) sent in `client.aio.models.generate_content(...)`.
   - `raw_output = response.text`.
   - `latency_ms` measured the same way.
   - `profile_snapshot` materialized the same way as Claude — inside the provider, before the SDK call.
   - `input_tokens` / `output_tokens` — Phase 2's `docs-researcher` is responsible for verifying the exact field names on `response.usage_metadata` in the version of `google-genai` this project pins. The implementation MUST wrap the read in `try/except AttributeError` and NULL both counts on any access failure. This way the slice ships safely even if the SDK's `usage_metadata` shape differs from what the docs-researcher reports, or evolves in the future.

5. **`ResumeGeneratorService.generate` (in `services/resume_generator.py`)
   destructures the tuple** and inserts the 9 breadcrumb columns alongside
   the existing fields in the `INSERT INTO generated_resumes` at lines 88-103.
   The provider has already materialized `profile_snapshot`, so this
   function just persists what it received — no second `json.dumps` here.

   **Ordering note:** the existing code calls
   `llm_service.analyze_and_generate(...)` at line 49 BEFORE
   `job_service.save_job_analysis(...)` at line 61. This ordering is
   preserved. The breadcrumbs feature does not change call order.

   **Orphan-row note:** the failure window between line 61 (jobs INSERT
   commits in its own transaction) and line 88 (resume INSERT in a
   separate transaction) is a pre-existing concern outside this slice's
   scope. Filed as `backlog/refined/resume-generation-atomicity.md`.

6. **`services/llm/__init__.py:_LazyLLMService.analyze_and_generate`
   return-type annotation** updates from `-> dict` to `-> tuple[dict, dict]`
   and the function forwards the provider's tuple directly. **CHECKLIST
   note:** this annotation change has no runtime test gate today
   (no type checker in CI). The IMPL_PLAN and CHECKLIST must list this
   as its own explicit line item so it doesn't get skipped during
   implementation. Type-checker enforcement is filed as
   `backlog/refined/ruff-ty-precommit.md`.

7. Test coverage:
   - `tests/test_claude_provider.py` — one new test asserting all 8
     provider-side breadcrumb fields land on the returned tuple from a
     mocked Anthropic SDK response with `usage.input_tokens` and
     `usage.output_tokens` populated. Existing tests adjusted to
     destructure the new tuple (e.g., `result, _ = await provider.analyze_and_generate(...)`).
   - `tests/test_gemini_provider.py` — analogous coverage. **Two**
     populated-path scenarios: one where `usage_metadata` exposes
     non-NULL token counts (under whatever field names docs-researcher
     pins), and one where access raises `AttributeError` (mock the
     attribute to be absent) and both counts come back NULL.
   - `tests/test_resumes.py` — extend `test_generate_resume_success`
     to use the tuple-returning mock shape, then assert the persisted
     row has non-NULL `provider`, `model`, `prompt_hash`, `raw_output`,
     `profile_snapshot`, `latency_ms`. Add an explicit assertion that
     `"photo" not in json.loads(row["profile_snapshot"]).get("personal_info", {})`
     — this pins the snapshot-timing requirement that Scenario 4 alone
     cannot catch.
   - `tests/test_resume_generator.py` — one new test that calls
     `resume_generator_service.generate` end-to-end with a mocked
     provider, queries the row via `get_db()`, and verifies
     `prompt_hash` and `profile_snapshot` are byte-identical across
     two generations against the same `(job_description, profile, language)`
     triple. This catches a hash that drifts due to a non-deterministic
     hash input or a snapshot that's not `sort_keys=True`.

8. The existing `migrations = [...]` list in `database.py:init_db` is the
   single insertion point for the additive ALTER TABLEs (see #1 above).
   The 9 new columns are appended to the end of that list.

9. `schemas.py` is **not** modified. The API response model
   (`GeneratedResumeResponse`) deliberately omits breadcrumbs — they are
   internal-only, consumed by future eval tooling via direct DB read.
   No route or Pydantic model is changed.

## Out

- Grading, rubric, scoring (lives in `llm-testing-framework`).
- Backfilling legacy rows (they stay NULL; retro skill handles "cannot grade" gracefully — already in scope for item 4).
- A `prompts` registry table or any change to how prompts are stored (item 2's territory).
- Surfacing breadcrumbs in any Svelte component or API response.
- Token-cost accounting in dollars.
- Migration framework (Alembic). The try/except ALTER TABLE pattern is sufficient for this slice; the structural refactor of `database.py` migrations is filed separately as `database-migration-refactor`.
- Cross-provider model-string normalization. Store what `_get_model()` returns verbatim.
- Wiring `prompt_path` to actual file paths under `prompts/resume-gen/`. Until item 2 lands, `prompt_path` is the sentinel string `"services/llm/base.py:SYSTEM_PROMPT"`.
- A `profile_snapshots` join table. JSON column is enough for v1.
- Capturing breadcrumbs on the failure path. The existing code only INSERTs the row on the success path; breadcrumbs are persisted only when a row is persisted.
- Closing the orphan-`jobs` failure window between the `save_job_analysis` commit and the `generated_resumes` INSERT. Filed as `resume-generation-atomicity`.
- Adding ruff / ty / any other linter or type checker to enforce annotation correctness. Filed as `ruff-ty-precommit`.

## Success criteria (all must hold)

After one fresh resume generation against either provider, the new row in
`generated_resumes` has non-NULL values for: `provider`, `model`,
`prompt_hash`, `raw_output`, `profile_snapshot`, `latency_ms`. Token counts
may be NULL on Gemini if `response.usage_metadata` access raises, and may
be NULL on Claude if the SDK returns None for the relevant fields.

**Migration-state-specific criteria** — the migration path differs by
starting DB state, and each path must produce the same final shape:

- **Fresh install** (`app.db` does not exist on disk): after `init_db()`
  runs, `generated_resumes` exists with all 9 breadcrumb columns plus the
  existing 12 columns plus `ON DELETE CASCADE` on the FK, zero rows. No
  `_migrate_*` function performs any work — they all early-return on the
  first call because the inline DDL produced the target shape directly.
  (NOTE: this is the success state. The inline DDL is being updated to
  match the post-migration shape so the recreate function's early-return
  fires correctly.)

- **Post-CASCADE upgrade path** (current production state — the table
  already has CASCADE and `language` / `job_analysis` / `user_id` from
  prior migrations): after `init_db()` runs, the 9 breadcrumb columns
  are appended via `ALTER TABLE`, existing rows are preserved with NULL
  in the new columns, no row is dropped or rewritten. The early-return
  at line 199 of `_migrate_generated_resumes_fk_cascade` fires.

- **Pre-CASCADE legacy path** (a hypothetical DB that predates the
  CASCADE migration — most likely a historical clone): `init_db()` runs
  `_migrate_generated_resumes_fk_cascade`, which does drop+recreate the
  table. Because the recreate block's CREATE/INSERT/SELECT column lists
  now include the 9 breadcrumb columns, the rebuild lands at the same
  final shape as the fresh install. Rows are rewritten **once**, into
  a target shape that already has the breadcrumb columns ready.

In **all three states**, calling `init_db()` a second time after the first
call succeeds is a no-op: zero `ALTER TABLE` errors (the try/except
swallows duplicate-column), zero recreate work (early-return fires), zero
row mutations.

**Functional / behavioral criteria:**

- For two generations against the same prompt text actually sent,
  `prompt_hash` is byte-identical on both rows. Verifies the hash is over
  the prompt sent, not memoized against a variable.
- For two generations against the same `(job_description, profile, language)`
  triple, `profile_snapshot` is byte-identical on both rows. Verifies
  `sort_keys=True` was used.
- `json.loads(row["profile_snapshot"]).get("personal_info", {})` does NOT
  contain a `"photo"` key. Verifies the snapshot was captured during the
  photo-stripped window (inside the provider, before the SDK call).
- `prompt_hash` is a hex SHA-1 string of length 40 with characters in `[0-9a-f]`.
- All existing tests in `tests/` still pass.
- The `/retro-prompts` skill can read every breadcrumb field from
  `SELECT * FROM generated_resumes` — verified by hand (no skill changes
  in this slice; that's item 4 of the initiative).

## BDD scenarios

### Scenario 1 — Fresh-DB migration adds columns idempotently

```
Given app.db does not exist on disk,
When init_db() runs,
Then generated_resumes is created with all 9 breadcrumb columns inline
  via the executescript CREATE TABLE,
And no _migrate_* function performs any drop/recreate
  (their early-returns fire because the inline DDL matches target shape),
And calling init_db() a second time succeeds with zero
  ALTER TABLE errors and zero recreate work.
```

### Scenario 1b — Post-CASCADE upgrade preserves rows

```
Given app.db is in the current production state
  (table has ON DELETE CASCADE, language, job_analysis, user_id, zero breadcrumb columns)
  And contains at least one existing row,
When init_db() runs,
Then ALTER TABLE ADD COLUMN appends the 9 breadcrumb columns,
  And the existing row is preserved with NULL in each new column,
  And _migrate_generated_resumes_fk_cascade's early-return at line 199 fires,
  And no DROP or recreate occurs.
```

### Scenario 2 — Claude success path persists every breadcrumb

```
Given the Claude provider is configured (LLM_PROVIDER=claude)
  And a valid profile with at least one work_experience and a photo
  And a valid 150+ char job_description,
When ResumeGeneratorService.generate completes successfully,
Then the new generated_resumes row has:
  provider = "claude"
  model = the value from CLAUDE_MODEL env or the default
  prompt_path = "services/llm/base.py:SYSTEM_PROMPT"
  prompt_hash = sha1 hex of (SYSTEM_PROMPT + "\n\n" + formatted user prompt), 40 chars in [0-9a-f]
  raw_output = the exact text from message.content[0].text
  profile_snapshot = json.dumps of the photo-stripped profile, sort_keys=True
    (verified by json.loads(row["profile_snapshot"]).get("personal_info", {})
     containing no "photo" key)
  latency_ms = a non-negative integer
  input_tokens = message.usage.input_tokens (an int or None — both valid)
  output_tokens = message.usage.output_tokens (an int or None — both valid).
```

### Scenario 3a — Gemini populated path persists token counts

```
Given the Gemini provider is configured (LLM_PROVIDER=gemini)
  And the Gemini SDK response object has a usage_metadata attribute
    with non-None values for the token-count fields (exact field names
    pinned by Phase 2 docs-researcher),
When breadcrumb capture runs,
Then input_tokens and output_tokens on the row reflect the SDK values,
And every other breadcrumb is populated correctly.
```

### Scenario 3b — Gemini SDK access failure leaves token counts NULL

```
Given the Gemini provider is configured
  And accessing response.usage_metadata.{prompt_token_count or candidates_token_count}
    raises AttributeError (mocked: usage_metadata absent or shape differs),
When breadcrumb capture runs,
Then input_tokens IS NULL on the row (not 0, not -1, not invented)
  And output_tokens IS NULL on the row,
And every other breadcrumb (provider, model, prompt_hash, raw_output,
  profile_snapshot, latency_ms) is still populated correctly.
```

### Scenario 4 — Determinism of prompt_hash and profile_snapshot

```
Given two consecutive successful generations
  against the same job_description, same profile, same language="en",
When both rows are inserted,
Then row1.prompt_hash == row2.prompt_hash byte-for-byte
  And row1.profile_snapshot == row2.profile_snapshot byte-for-byte.
```

### Scenario 5 — Mid-call exception writes no breadcrumb row

```
Given the LLM provider raises (e.g., anthropic.APIConnectionError)
  at some point during analyze_and_generate,
When the exception propagates out of ResumeGeneratorService.generate,
Then no row is INSERTed into generated_resumes,
And the existing test in tests/test_resumes.py that asserts
  "no row created on LLM error" continues to pass without modification.
```

(Pre-existing concerns about orphan rows in the `jobs` table on this
failure path are tracked separately in
`backlog/refined/resume-generation-atomicity.md` and are out of scope here.)

## Non-functional notes

- Latency measurement uses `time.monotonic()` (not `time.time()`) so a wall-clock jump during the call doesn't produce a negative or garbage `latency_ms`. `int(delta * 1000)` may legitimately equal 0 on a mocked sub-millisecond call — `>= 0` is the correct assertion, not `> 0`.
- `prompt_hash` is SHA-1, not SHA-256: matches the "fingerprint, not cryptographic" use case and keeps the column short. Item 3's importer treats it as an opaque equality token; collision resistance is not required.
- `profile_snapshot` uses `ensure_ascii=False` and `sort_keys=True` so the JSON is human-readable in a sqlite browser AND byte-equal across runs.
- The provider — not the caller — materializes `profile_snapshot`. Reasoning: the provider is the only code that sees the photo-stripped dict at the exact moment of the SDK call. Putting the snapshot capture inside the provider closes the timing-ambiguity hole the analysis-reviewer surfaced.
- The 9 new columns add zero indexes. They are written once on INSERT and read by external tooling only.
- No env var, feature flag, or runtime toggle. Breadcrumbs are always captured on the success path.
