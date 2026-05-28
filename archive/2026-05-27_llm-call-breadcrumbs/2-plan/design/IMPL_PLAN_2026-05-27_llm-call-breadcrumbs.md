# IMPL_PLAN — llm-call-breadcrumbs

**Slug:** llm-call-breadcrumbs
**Date:** 2026-05-27
**Ceremony:** M
**Spec:** `workbench/1-analyze/spec/FEATURE_SPEC_2026-05-27_llm-call-breadcrumbs.md`
**Library notes:**
- `workbench/2-plan/research/LIBRARY_NOTES_anthropic_2026-05-27.md`
- `workbench/2-plan/research/LIBRARY_NOTES_google-genai_2026-05-27.md`
**Ecosystem decision:** `workbench/2-plan/research/ECOSYSTEM_DECISION_2026-05-27_llm-call-breadcrumbs.md`

---

## Strategy in one paragraph

The provider — not the caller — owns the breadcrumbs. Each provider returns a `tuple[dict, dict]` where the second element is a fully-populated breadcrumbs dict. The caller (`ResumeGeneratorService.generate`) destructures and persists. This puts the snapshot capture inside the same code that knows what the LLM actually received (post-photo-strip). The database migration touches four locations in `database.py` so that fresh installs and the recreate path both end at the same target shape. Token-count reads are defensive on Gemini (per `LIBRARY_NOTES_google-genai`: `usage_metadata` and its sub-fields are all `Optional`) and direct on Claude (per `LIBRARY_NOTES_anthropic`: `input_tokens` and `output_tokens` are bare `int`, never None on success).

---

## File-by-file plan

### 1. `database.py` — schema migration (four locations)

**Modify, not create.** The file already exists; all edits are surgical.

**1a. Inline DDL at `database.py:339-353`** — `CREATE TABLE IF NOT EXISTS generated_resumes`:

Append 9 column declarations BEFORE the `FOREIGN KEY` clause:

```
prompt_path TEXT,
prompt_hash TEXT,
provider TEXT,
model TEXT,
profile_snapshot TEXT,
raw_output TEXT,
latency_ms INTEGER,
input_tokens INTEGER,
output_tokens INTEGER,
```

(All nullable by default. No DEFAULT clause — the migration writes them on
first INSERT after the feature lands; legacy rows stay NULL.)

**1b. Migrations list at `database.py:357-376`** — append 9 entries to the
`migrations = [...]` list, one per column, each in the same `ALTER TABLE
generated_resumes ADD COLUMN <name> <type>` shape as the existing entries.
Order matches 1a. Appended AT THE END so any production DB that already
ran prior migrations doesn't get insertion-order shift.

**1c. `_migrate_generated_resumes_fk_cascade` CREATE block at `database.py:207-222`** —
add the 9 column declarations to the `CREATE TABLE
generated_resumes_new (...)` SQL, in the same position as 1a (before FK
clause).

**1d. `_migrate_generated_resumes_fk_cascade` INSERT/SELECT block beginning at `database.py:228` (block runs through line 236)** —
add the 9 column names to both the INSERT target list and the SELECT
source list, in matching order. The SELECT will pull from
`generated_resumes` which by this point has the columns (via 1b's ALTERs
running before this function at line 441).

**Risk:** all four locations must stay in sync. Mitigation: the
checklist-builder will list each location as a separate checkbox.

### 2. `services/llm/base.py` — Protocol shape change

**Modify.** Two edits:

**2a.** Update `analyze_and_generate` return-type annotation from `dict`
to `tuple[dict, dict]` and update the docstring's Returns section to
describe both elements: parsed JSON, and the breadcrumbs dict with the
8 provider-owned fields (provider, model, prompt_path, prompt_hash,
raw_output, latency_ms, input_tokens, output_tokens). `profile_snapshot`
is listed as the 9th field in the breadcrumbs dict (also provider-owned;
both providers materialize it identically).

**2b.** No other change. `SYSTEM_PROMPT` / `USER_PROMPT_TEMPLATE` /
`LANGUAGE_INSTRUCTIONS` stay verbatim. Items 2/3/4 of the initiative
will refactor those out into prompt files; that's not this slice.

### 3. `services/llm/claude.py` — implement breadcrumbs

**Modify `ClaudeProvider.analyze_and_generate`.** The new flow:

```
profile_json = json.dumps(profile, indent=2)             # existing
language_instruction = LANGUAGE_INSTRUCTIONS.get(...)   # existing
user_prompt = USER_PROMPT_TEMPLATE.format(...)          # existing

profile_snapshot = json.dumps(profile, sort_keys=True, ensure_ascii=False)
prompt_text = SYSTEM_PROMPT + "\n\n" + user_prompt
prompt_hash = hashlib.sha1(prompt_text.encode("utf-8")).hexdigest()
model_id = _get_model()

t0 = time.monotonic()
try:
    message = await client.messages.create(...)         # existing args, no change
except (existing exception chain — re-raise as before)
latency_ms = int((time.monotonic() - t0) * 1000)

response_text = message.content[0].text                  # existing
# ... existing JSON-extract logic produces `result` ...

breadcrumbs = {
    "provider": "claude",
    "model": model_id,
    "prompt_path": "services/llm/base.py:SYSTEM_PROMPT",
    "prompt_hash": prompt_hash,
    "raw_output": response_text,
    "latency_ms": latency_ms,
    "input_tokens": message.usage.input_tokens,          # always int per LIBRARY_NOTES_anthropic
    "output_tokens": message.usage.output_tokens,        # always int per LIBRARY_NOTES_anthropic
    "profile_snapshot": profile_snapshot,
}
return result, breadcrumbs
```

**Key call-outs:**
- `profile_snapshot` is materialized at the top of the function, BEFORE
  the SDK call. The dict `profile` reference is the same the caller will
  later restore the photo into — by capturing now, we freeze the
  photo-stripped state. Verified against `services/resume_generator.py:34-53`
  where the dict is photo-stripped before the call and restored after.
- `prompt_hash` uses SHA-1 over `system + "\n\n" + user_prompt`. This
  exact concatenation lets the hash match what Gemini's hash would be
  for the same inputs (Gemini already concatenates with `"\n\n"` at
  `services/llm/gemini.py:76`), so cross-provider replay tooling sees
  matching hashes if the same prompts and inputs were used.
- `latency_ms` is measured around the SDK call ONLY, not around JSON
  parsing. JSON parsing is local CPU work and not relevant to
  cost/latency comparison.
- Error paths are unchanged. The new variables (`t0`, `profile_snapshot`,
  `prompt_hash`, `model_id`, `prompt_text`) are local. If an exception
  fires after they're set but before `breadcrumbs` is returned, the
  exception propagates and no row is INSERTed (caller doesn't reach the
  INSERT — see #5). This matches Scenario 5 of the spec.

Imports to add at top of file:
- `import time` (for `time.monotonic()`)
- `import hashlib` (for SHA-1)
- `import json` is already present at line 4 — no addition needed.

### 4. `services/llm/gemini.py` — implement breadcrumbs

**Modify `GeminiProvider.analyze_and_generate`.** Same pattern as Claude
with the SDK-specific token-read pattern from `LIBRARY_NOTES_google-genai`:

```
# existing prelude — profile_json, language_instruction, full_prompt
profile_snapshot = json.dumps(profile, sort_keys=True, ensure_ascii=False)
prompt_hash = hashlib.sha1(full_prompt.encode("utf-8")).hexdigest()
model_id = _get_model()

t0 = time.monotonic()
try:
    response = await client.aio.models.generate_content(...)  # existing
except (existing exception chain)
latency_ms = int((time.monotonic() - t0) * 1000)

response_text = response.text                              # existing
# ... existing JSON-extract logic produces `result` ...

usage = getattr(response, "usage_metadata", None)
if usage is not None:
    input_tokens = usage.prompt_token_count if usage.prompt_token_count is not None else None
    output_tokens = usage.candidates_token_count if usage.candidates_token_count is not None else None
else:
    input_tokens = None
    output_tokens = None

breadcrumbs = {
    "provider": "gemini",
    "model": model_id,
    "prompt_path": "services/llm/base.py:SYSTEM_PROMPT",
    "prompt_hash": prompt_hash,
    "raw_output": response_text,
    "latency_ms": latency_ms,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "profile_snapshot": profile_snapshot,
}
return result, breadcrumbs
```

**Key call-outs:**
- Token reads use a two-level guard: `getattr` for the `usage_metadata`
  attribute, then `is not None` for each sub-field. Per
  `LIBRARY_NOTES_google-genai`, both layers can be missing on error
  responses, safety-blocked responses, and certain streaming chunks.
  The spec's `try/except AttributeError` pattern *would* catch attribute
  absence (including `usage_metadata is None`, since attribute access
  on `None` raises `AttributeError`), but it would NOT catch sub-field
  values that are `int | None = None`. The explicit two-level guard in
  this plan also covers that case.
- The library notes flagged residual uncertainty on the spelling of
  `candidates_token_count` (could be singular `candidate_token_count`).
  **Build-phase verification step:** before declaring the feature done,
  run one real Gemini generation (or a unit test against a real-shape
  mock built from `vars(response.usage_metadata)`) and confirm the
  attribute exists. If the spelling is singular, change one line in
  the code and one in `LIBRARY_NOTES_google-genai`. This is a
  20-second check, not a blocker — the defensive guards ensure the
  spelling error degrades to NULL rather than breaking the call.
- Same imports to add: `time`, `hashlib`. `json` already present.

### 5. `services/llm/__init__.py` — wrapper annotation + forwarding

**Modify `_LazyLLMService.analyze_and_generate`:**

5a. Change return annotation `-> dict` to `-> tuple[dict, dict]`.
5b. Change the docstring's Returns section to describe the tuple.
5c. The function body already forwards via `await
self._get_instance().analyze_and_generate(...)` — no body change needed,
just the annotation and docstring. The provider's tuple flows through
unchanged.

**Explicit CHECKLIST line:** this annotation change has no test gate
(no type checker in CI). Implementer must verify by hand that the new
annotation matches `tuple[dict, dict]` literally and the docstring is
updated.

### 6. `services/resume_generator.py` — destructure and persist

**Modify `ResumeGeneratorService.generate`.** Three edits:

**6a.** Change line 49 from:
```
llm_result = await llm_service.analyze_and_generate(...)
```
to:
```
llm_result, breadcrumbs = await llm_service.analyze_and_generate(...)
```

The variable name `llm_result` is preserved everywhere downstream — no
ripple through the rest of the function. `breadcrumbs` is a new local.

**6b.** Extend the `INSERT INTO generated_resumes` at lines 88-103 to
include the 9 new columns and their values from the `breadcrumbs` dict:

```
cursor = conn.execute(
    """
    INSERT INTO generated_resumes
    (job_id, job_title, company_name, match_score, resume_content,
     language, job_analysis,
     prompt_path, prompt_hash, provider, model, profile_snapshot,
     raw_output, latency_ms, input_tokens, output_tokens)
    VALUES (?, ?, ?, ?, ?, ?, ?,  ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        saved_job_id,
        llm_result.get("job_title"),
        llm_result.get("company_name"),
        llm_result.get("match_score"),
        json.dumps(resume_content),
        language,
        job_analysis_json,
        breadcrumbs["prompt_path"],
        breadcrumbs["prompt_hash"],
        breadcrumbs["provider"],
        breadcrumbs["model"],
        breadcrumbs["profile_snapshot"],
        breadcrumbs["raw_output"],
        breadcrumbs["latency_ms"],
        breadcrumbs["input_tokens"],
        breadcrumbs["output_tokens"],
    ),
)
```

Column order in INSERT matches the appended order in the inline DDL (#1a)
and the migrations list (#1b). The parameter binding uses direct dict
indexing (not `.get(..., None)`) — every key in `breadcrumbs` is
guaranteed populated by the provider (see #3 and #4). Missing key would
be a programmer error, not runtime data.

**6c.** No change to call order. LLM call still happens at line 49 BEFORE
`save_job_analysis` at line 61. The orphan-`jobs`-row failure window is
out of scope (filed as `resume-generation-atomicity`).

### 7. `tests/test_claude_provider.py` — destructure + add coverage

**Modify, not create.**

**7a.** Every existing test that calls
`await claude_provider.analyze_and_generate(...)` and reads the return
as a single `result` value must destructure. Pattern:

```
result, _ = await claude_provider.analyze_and_generate(...)
```

(The `_` discards breadcrumbs in tests that only care about parsed output.)

Tests to touch in this file:
- `test_successful_generation`
- `test_extracts_json_from_mixed_response`
- `test_language_parameter_passed`
- (Error-path tests don't reach the return — they assert on raise. No change.)

**7b.** Add new test `test_breadcrumbs_populated_on_success`:
- Mock `_get_client` to return an `AsyncMock` whose `messages.create`
  returns a `MagicMock` with `content[0].text` set to a valid JSON
  string AND `usage.input_tokens = 1234` AND `usage.output_tokens = 567`.
- Call `await claude_provider.analyze_and_generate(jd, profile)`.
- Destructure the tuple.
- Assert breadcrumbs dict has:
  - `provider == "claude"`
  - `model == _get_model()` (or the default the test's env produces)
  - `prompt_path == "services/llm/base.py:SYSTEM_PROMPT"`
  - `prompt_hash` is 40 chars, all in `[0-9a-f]`, matches expected sha1
  - `raw_output` equals the mocked text
  - `latency_ms >= 0`
  - `input_tokens == 1234`
  - `output_tokens == 567`
  - `profile_snapshot` is valid JSON and round-trips via `json.loads(...)`
    to the dict the provider received.

**Provider-vs-integration contract for `profile_snapshot` (important):**
The provider's job is "snapshot what I received." If the caller passes a
profile without a `photo` key, the snapshot has no photo. If the caller
passes a profile WITH a `photo`, the snapshot DOES contain the photo —
that is the provider behaving correctly. The photo-stripping is the
caller's responsibility (it happens in `services/resume_generator.py:41`
before the call). So:
- The provider unit test (`test_breadcrumbs_populated_on_success` here)
  passes a profile WITHOUT a photo, asserts the snapshot also lacks one.
  Optionally a second provider unit test passes a profile WITH a photo
  and asserts the snapshot also has the photo — provider contract test.
- The integration test (`test_profile_snapshot_omits_photo` in §10b)
  goes through `resume_generator_service.generate(...)` end-to-end with
  a photo in the profile, and asserts the snapshot DOES NOT contain the
  photo. This verifies the caller stripped correctly AND the provider
  snapshot-timed correctly (it captured the post-strip state, before
  the caller's `services/resume_generator.py:53` restored the photo).

Per `LIBRARY_NOTES_anthropic`, no NULL-branch test is needed for Claude
tokens (the SDK always returns int).

### 8. `tests/test_gemini_provider.py` — destructure + add coverage

**Modify.** Same destructuring as #7a applied to the existing happy-path
tests:
- `test_successful_generation`
- `test_extracts_json_from_response`
- `test_uses_custom_model_from_env`

Add two new tests:

**8a. `test_breadcrumbs_populated_with_usage_metadata`** — mock the
response object to have `usage_metadata.prompt_token_count = 100` and
`usage_metadata.candidates_token_count = 50`. Assert breadcrumbs:
- `provider == "gemini"`
- `model == "gemini-2.5-flash"` (or mocked value)
- `prompt_path == "services/llm/base.py:SYSTEM_PROMPT"`
- `prompt_hash` is a 40-char hex sha1
- `input_tokens == 100`
- `output_tokens == 50`
- `latency_ms >= 0`
- `profile_snapshot` round-trips to a dict

**8b. `test_breadcrumbs_tokens_null_when_usage_metadata_missing`** —
mock the response to NOT have a `usage_metadata` attribute (use a plain
`MagicMock` with `usage_metadata` configured to `None`, or use
`spec=...` on the MagicMock to make it raise on attribute access — pick
whichever produces the cleanest test). Assert:
- `input_tokens is None`
- `output_tokens is None`
- Other breadcrumbs populated normally.

Optionally add **8c. `test_breadcrumbs_tokens_null_when_subfield_is_none`** —
`usage_metadata` exists but `prompt_token_count` is None. Assert NULL
fall-through. This catches the case `LIBRARY_NOTES_google-genai`
explicitly warned about (sub-field-level None).

### 9. `tests/test_resumes.py` — assert breadcrumbs persist

**Modify `test_generate_resume_success`** (existing test at line 51).

The current mock returns a single dict. Change it to a `(dict, dict)`
tuple matching the new shape:

```
mock_llm.return_value = (
    {  # parsed (existing structure preserved)
        "job_title": "Software Engineer",
        ... existing keys ...
    },
    {  # breadcrumbs
        "provider": "claude",
        "model": "claude-test-model",
        "prompt_path": "services/llm/base.py:SYSTEM_PROMPT",
        "prompt_hash": "a" * 40,
        "raw_output": '{"job_title": "Software Engineer", ...}',
        "latency_ms": 42,
        "input_tokens": 1000,
        "output_tokens": 500,
        "profile_snapshot": '{"personal_info": {"full_name": "Jane"}, ...}',
    },
)
```

Then after the existing success assertions, add:

```
with get_db() as conn:
    row = conn.execute(
        "SELECT * FROM generated_resumes WHERE id = ?", (result["id"],)
    ).fetchone()
    assert row["provider"] == "claude"
    assert row["model"] == "claude-test-model"
    assert row["prompt_hash"] == "a" * 40
    assert row["raw_output"] is not None
    assert row["profile_snapshot"] is not None
    snap = json.loads(row["profile_snapshot"])
    assert "photo" not in snap.get("personal_info", {})
    assert row["latency_ms"] == 42
    assert row["input_tokens"] == 1000
    assert row["output_tokens"] == 500
```

Other resume tests in this file that mock `analyze_and_generate` must
similarly switch their `mock_llm.return_value` to the tuple shape, even
when they don't assert on breadcrumbs. The destructure in
`services/resume_generator.py` at line 49 will fail with "cannot unpack
non-iterable dict" otherwise.

**Test-mock sweep — HIGH-certainty, ~43 occurrences across 6 files.**

Plan-reviewer flagged the original "MEDIUM, ≥2 occurrences" estimate as
off by ~5×. Confirmed by `grep -c "analyze_and_generate" tests/*.py`:

| File | Count | What they mock | Action |
|---|---|---|---|
| `tests/test_resumes.py` | 15 | `@patch("services.resume_generator.llm_service.analyze_and_generate")` with `mock_llm.return_value = {...}` | Update return-value to `(dict, dict)` tuple shape |
| `tests/test_pdf_api.py` | 8 | same `@patch(...)` decorator | Update return-value to tuple |
| `tests/test_resume_generator.py` | 6 | same | Update return-value to tuple |
| `tests/test_chronological_order.py` | 3 | same | Update return-value to tuple |
| `tests/test_jobs.py` | 1 | same | Update return-value to tuple |
| `tests/test_llm_service.py` | 10 | Mocks at SDK level (`_get_client`) but assigns `result = await llm_service.analyze_and_generate(...)` — assignment now receives a tuple | Destructure `result, _ = await ...` at each call site |

**Plus the two provider tests (already enumerated in §7 and §8):**

| File | Count | What they mock | Action |
|---|---|---|---|
| `tests/test_claude_provider.py` | 8 (3 happy-path + 5 error-path) | Mocks `_get_client`; assigns `result = await provider.analyze_and_generate(...)` on happy paths | Destructure `result, _ = await ...` on the 3 happy paths only — error paths don't reach the return |
| `tests/test_gemini_provider.py` | 10 (3 happy-path + 7 error-path) | same | Destructure on the 3 happy paths only |

**Total mechanical edits: ~33 mock `return_value` updates + ~6 destructure
updates. Add ~3 net-new tests (breadcrumb assertions in test_resumes.py,
provider-test additions in §7b / §8a / §8b).**

For each `return_value = {...}` in the 5 caller-level files
(test_resumes, test_pdf_api, test_resume_generator,
test_chronological_order, test_jobs), the implementer can either:

1. Update each one to return `(existing_dict, sentinel_breadcrumbs)`
   where `sentinel_breadcrumbs` is a small constant dict at module
   level (DRY across the file), OR
2. Define a `conftest.py`-level helper `wrap_llm_result(parsed)` that
   produces the tuple shape from a parsed dict, so each test changes
   from `mock_llm.return_value = {...}` to
   `mock_llm.return_value = wrap_llm_result({...})`.

Option 2 is cleaner if conftest.py is acceptable to touch; option 1 is
mechanical. The implementer picks based on local readability — both are
correct. Either way, the sweep must be **exhaustive** — every one of
the ~33 occurrences must be updated, or `uv run pytest -q` fails with
TypeError on first hit.

### 10. `tests/test_resume_generator.py` — determinism + snapshot-without-photo

**Add.** Two new tests:

**10a. `test_prompt_hash_deterministic_across_runs`** — mock the
provider's `analyze_and_generate` to return a static tuple. Call
`resume_generator_service.generate(...)` twice with the same JD,
profile, language. Query both rows. Assert `row1["prompt_hash"] ==
row2["prompt_hash"]` and `row1["profile_snapshot"] ==
row2["profile_snapshot"]`.

(Determinism comes from the provider's static return in this test, but
the persistence path is still exercised — confirms the caller doesn't
mangle the breadcrumbs between provider return and INSERT.)

**10b. `test_profile_snapshot_omits_photo`** — set up a profile with
a `personal_info.photo` field (a small base64 string). Mock the
provider to capture what it RECEIVES and put that into the breadcrumbs'
`profile_snapshot`, then return the tuple. Call `generate(...)`. Query
the row. Assert:

```
snap = json.loads(row["profile_snapshot"])
assert "photo" not in snap.get("personal_info", {})
```

This is the integration test that closes the snapshot-timing concern
from analysis-reviewer Issue #2. It exercises both the
`services/resume_generator.py:41` photo-strip AND the provider's
materialization of `profile_snapshot` from the photo-stripped dict.

### 10c. `tests/test_resume_generator.py` — mid-call exception writes no row (NEW TEST, addresses ISSUE-2)

**Add `test_no_row_inserted_on_llm_exception`** to `tests/test_resume_generator.py`.

The plan-reviewer correctly flagged that the spec's Scenario 5 referenced
an "existing test" that does not exist. No test in `tests/` exercises
`ResumeGeneratorService.generate` through a path where the LLM provider
raises and asserts zero rows are INSERTed into `generated_resumes`.
Rather than remove the gate, add the test.

```python
@pytest.mark.asyncio
async def test_no_row_inserted_on_llm_exception(client):
    """Scenario 5: LLM provider raises → no breadcrumb row written."""
    _create_work_experience(client)  # or whatever the helper is

    initial_count = _count_resume_rows()  # SELECT COUNT(*) FROM generated_resumes

    with patch(
        "services.resume_generator.llm_service.analyze_and_generate",
        new_callable=AsyncMock,
    ) as mock_llm:
        mock_llm.side_effect = ConnectionError("simulated provider failure")

        with pytest.raises(ConnectionError):
            await resume_generator_service.generate(
                job_description="A" * 150,
                language="en",
            )

    assert _count_resume_rows() == initial_count, \
        "no row should be written when the LLM provider raises"
```

The helper `_count_resume_rows()` uses `get_db()` to `SELECT COUNT(*) FROM
generated_resumes`. If a similar helper already exists in
`test_resume_generator.py`, reuse it; otherwise inline the query.

This raises the new-test count from 5 to 6 (one new test per IMPL_PLAN
sections 7b, 8a, 8b, 10a, 10b, **10c**). Net delta ~15 LOC.

### 11. `tests/test_database_migrations.py` — NEW file (small)

**Create.** One file, two short tests:

**11a. `test_fresh_install_includes_breadcrumb_columns`** — use a
temp file or `:memory:` DB, call `database.init_db()` against a
monkey-patched `DATABASE = "/tmp/test_fresh.db"` (delete first if
exists), then introspect:

```
cursor = conn.execute("PRAGMA table_info(generated_resumes)")
cols = {row[1] for row in cursor.fetchall()}
for col in (
    "prompt_path", "prompt_hash", "provider", "model",
    "profile_snapshot", "raw_output", "latency_ms",
    "input_tokens", "output_tokens",
):
    assert col in cols, f"missing column: {col}"
```

**11b. `test_init_db_idempotent_with_breadcrumb_columns`** — run
`init_db()` twice in a row against the same DB file. Assert no
exception, assert column set unchanged.

**11c. `test_recreate_path_preserves_breadcrumb_columns`** (NEW, addresses ISSUE-3)

Plan-reviewer correctly flagged that §1c and §1d add code specifically
for the `_migrate_generated_resumes_fk_cascade` recreate path, but no
test in this slice exercises that path. The risks-table mitigation
("Test #11a covers fresh install") was wrong — fresh install hits the
new inline DDL directly and doesn't enter the recreate function (its
early-return at line 200 fires because the inline DDL now produces the
CASCADE shape). So §1c/§1d code is unverified.

Add a forcing test that:

1. Creates a temp DB.
2. Manually executes the **legacy pre-CASCADE** `CREATE TABLE generated_resumes`
   SQL (the original 2024 shape from `database.py:339-353` BEFORE this
   slice's changes). This is hard-coded as a string in the test — copied
   verbatim from `git show HEAD:database.py | sed -n '339,353p'` and
   committed inline. The test seeds one row with non-null values for
   `job_description_id`, `job_title`, `company_name`, `match_score`,
   `resume_content`.
3. Sets `DATABASE` to point at this DB (via monkeypatch on
   `database.DATABASE`), then calls `init_db()`.
4. Asserts:
   - The recreate path DID run (verify by checking the table's `sqlite_master.sql`
     contains `ON DELETE CASCADE` after init_db).
   - All 9 breadcrumb columns exist on the resulting table (`PRAGMA table_info`).
   - The seeded row survived with breadcrumb columns NULL and original
     values preserved.

```python
def test_recreate_path_preserves_breadcrumb_columns(tmp_path, monkeypatch):
    """Forced pre-CASCADE → CASCADE migration must carry breadcrumb columns
    through the recreate. Verifies §1c and §1d patches."""
    db_path = tmp_path / "legacy.db"
    monkeypatch.setattr("database.DATABASE", str(db_path))

    # Seed the legacy pre-CASCADE shape directly (no FK CASCADE, no language, etc.)
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            title TEXT DEFAULT 'Untitled Job',
            company_name TEXT,
            user_id INTEGER DEFAULT 1
        );
        INSERT INTO jobs (id, original_text) VALUES (1, 'legacy JD');
        CREATE TABLE generated_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description_id INTEGER NOT NULL,
            job_title TEXT,
            company_name TEXT,
            match_score REAL,
            resume_content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_description_id) REFERENCES jobs(id)
        );
        INSERT INTO generated_resumes
        (job_description_id, job_title, resume_content)
        VALUES (1, 'Test Engineer', '{}');
    """)
    conn.commit()
    conn.close()

    # Run init_db — should trigger the recreate path
    from database import init_db
    init_db()

    conn = sqlite3.connect(db_path)
    # Verify CASCADE landed
    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='generated_resumes'"
    )
    table_sql = cursor.fetchone()[0]
    assert "ON DELETE CASCADE" in table_sql

    # Verify all 9 breadcrumb columns present after recreate
    cursor = conn.execute("PRAGMA table_info(generated_resumes)")
    cols = {row[1] for row in cursor.fetchall()}
    for col in (
        "prompt_path", "prompt_hash", "provider", "model",
        "profile_snapshot", "raw_output", "latency_ms",
        "input_tokens", "output_tokens",
    ):
        assert col in cols, f"missing breadcrumb column after recreate: {col}"

    # Verify seeded row survived with breadcrumb columns NULL
    cursor = conn.execute(
        "SELECT job_title, prompt_hash FROM generated_resumes WHERE id = 1"
    )
    row = cursor.fetchone()
    assert row[0] == "Test Engineer"
    assert row[1] is None
    conn.close()
```

This is the smoke test that closes the "untested defensive code" gap.
Net delta: ~50 LOC including the legacy-shape seed SQL (which is
necessarily verbose because it has to be a verbatim historical CREATE
TABLE statement).

(The post-CASCADE upgrade-path test is deliberately still out of scope —
it belongs to `database-migration-refactor`. This slice tests:
fresh install (§11a), idempotent re-run (§11b), and forced pre-CASCADE
legacy recreate (§11c, NEW).)

---

## Library patterns to use (citations)

- **anthropic** (per `LIBRARY_NOTES_anthropic_2026-05-27.md`):
  `message.usage.input_tokens` and `message.usage.output_tokens` are
  bare `int` on a successful `Message`. Read directly, no None guard.
  `message.content[0].text` is canonical for non-streaming.
- **google-genai** (per `LIBRARY_NOTES_google-genai_2026-05-27.md`):
  use `usage = getattr(response, "usage_metadata", None)` then guard
  each sub-field with `is not None`. Field names:
  `prompt_token_count`, `candidates_token_count`. Live verification
  step during build to confirm plural spelling.
- **hashlib** (Python stdlib): `hashlib.sha1(prompt_text.encode("utf-8")).hexdigest()`
  produces a 40-char hex string. No third-party dep needed.
- **time** (Python stdlib): `time.monotonic()` returns a float in
  seconds; `int((t1 - t0) * 1000)` yields integer milliseconds.
- **json** (Python stdlib): `json.dumps(profile, sort_keys=True,
  ensure_ascii=False)` produces deterministic, human-readable JSON.

## Lean-code rule compliance per file

Per `CLAUDE.md`:
- All new functions follow `{verb}{ScopeInMaxThreeWords}` naming.
  Specific verbs added: none (we are MODIFYING existing methods, not
  creating new ones). Existing methods (`analyze_and_generate`,
  `generate`, etc.) stay named as-is — the lean-code rules apply to
  *new* code; existing names are out of scope.
- All NEW test helper functions, if any, must use permitted verbs.
- File headers stay unchanged on existing files — they already have
  their docstrings; we're modifying not rewriting.
- New test file `tests/test_database_migrations.py` gets a docstring
  header matching the style of sibling test files (one-line module
  docstring describing scope).
- No `// XYZ for now` or `// TODO` comments added anywhere.
- No abbreviations: variable names use full words
  (`prompt_text`, `model_id`, `latency_ms`, not `pt`, `m`, `lat`).

---

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| `candidates_token_count` is actually singular `candidate_token_count` | LOW (per LIBRARY_NOTES, JS SDK confirms plural) | Defensive guards mean wrong spelling degrades to NULL; build-phase live check confirms |
| Forgetting one of the four `database.py` locations | MEDIUM | checklist-builder lists each as separate checkbox; plan-reviewer will verify all four paths are named |
| Forgetting to destructure in existing tests | HIGH (~43 occurrences across 6 files — confirmed by grep, see §9 sweep table) | Per-file enumeration in §9; CHECKLIST §4.4 has explicit row per file; `uv run pytest -q` failure is loud and immediate on any miss |
| `profile_snapshot` accidentally contains photo because caller mutation timing changed | LOW | Test `test_profile_snapshot_omits_photo` (#10b) catches this; provider-side capture means provider holds the line |
| SQLite recreate path (§1c/§1d) ships as untested defensive code | RESOLVED | NEW test #11c forces a pre-CASCADE seed and asserts breadcrumb columns survive the recreate; closes the plan-reviewer gap |
| Scenario 5 (mid-call exception → no row) referenced a phantom test | RESOLVED | NEW test #10c added; raises new-test count to 7 (or 8 with optional 8c) |

## Test plan summary

- **New tests: 7** —
  1. §7b `test_breadcrumbs_populated_on_success` (Claude)
  2. §8a `test_breadcrumbs_populated_with_usage_metadata` (Gemini happy)
  3. §8b `test_breadcrumbs_tokens_null_when_usage_metadata_missing` (Gemini)
  4. §8c `test_breadcrumbs_tokens_null_when_subfield_is_none` (Gemini) — optional but recommended
  5. §10a `test_prompt_hash_deterministic_across_runs`
  6. §10b `test_profile_snapshot_omits_photo`
  7. §10c `test_no_row_inserted_on_llm_exception` (NEW, addresses ISSUE-2)
  8. §11a `test_fresh_install_includes_breadcrumb_columns`
  9. §11b `test_init_db_idempotent_with_breadcrumb_columns`
  10. §11c `test_recreate_path_preserves_breadcrumb_columns` (NEW, addresses ISSUE-3)
  (Counting §8c as optional: 9 required + 1 optional = 10 net new test functions; conservative bound is 9.)
- **Modified tests: ~33** destructuring updates across 6 files (see §9 sweep table)
- Net delta: ~250 LOC test code added (originally estimated ~150; the sweep + the two new tests bring it up)
- All tests run via `uv run pytest -q`
- Pre-existing test count must remain identical (no test deletion)

## Implementation order

1. `database.py` migration — gate everything else (without it, INSERTs fail)
2. `services/llm/base.py` — Protocol annotation
3. `services/llm/claude.py` — implement breadcrumbs (Claude tested first because docs are firm)
4. `services/llm/gemini.py` — implement breadcrumbs (Gemini tested second; live `vars()` check for spelling)
5. `services/llm/__init__.py` — wrapper annotation + docstring
6. `services/resume_generator.py` — destructure and persist
7. `tests/test_claude_provider.py` + `tests/test_gemini_provider.py` — provider-level tests
8. `tests/test_resumes.py` + `tests/test_resume_generator.py` — integration tests
9. `tests/test_database_migrations.py` — migration tests
10. Run `uv run pytest -q` end-to-end; iterate
