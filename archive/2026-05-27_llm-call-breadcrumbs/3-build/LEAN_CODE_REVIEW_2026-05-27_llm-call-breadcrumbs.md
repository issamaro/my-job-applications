---
feature: llm-call-breadcrumbs
date: 2026-05-27
status: ISSUES
reviewer: lean-code-reviewer
diff_base: HEAD
files_reviewed: 16
---

# Lean Code Review — llm-call-breadcrumbs

Scope: this review covers only code newly introduced or modified by the
breadcrumbs feature. Pre-existing repo drift (e.g. the `analyze_and_generate`
verb on `LLMProvider`, `ResumeGeneratorService`, `_LazyLLMService`, the
docstrings on existing provider methods, the various `# Restore photo …`
inline comments already in `services/resume_generator.py`) is noted only when
the new diff touches the surrounding lines. It is not re-litigated.

Tests follow the brief's pragmatism allowance: pytest test names are exempt
from the verb whitelist; test docstrings are allowed.

---

## Verb violations

| file:line | declared_name | forbidden_verb | suggested_verb | severity |
|---|---|---|---|---|
| tests/test_resume_generator.py:330 | `_count_resume_rows` | `count` (not in 9-verb whitelist) | `read_resume_row_count` (verb `read`) | MAJOR |
| tests/test_resume_generator.py:400 | `capture_and_return` | `capture` AND `return` (neither permitted; also two verbs) | split or rename to `read_profile_snapshot` | MAJOR |

Notes:
- `create_llm_result` (tests/conftest.py:33) — verb `create` is permitted, scope two words (`llm result`). `llm` is established as a namespace-level noun by the existing `services/llm/` package; it is not a fresh abbreviation introduced by this feature. PASS.
- Pre-existing `analyze_and_generate` on the Protocol and providers is untouched in spirit by this feature — the signature changed, the name did not. Flagged as repo drift below but not as a new violation.

## Scope-size violations

| file:line | name | words_after_verb |
|---|---|---|
| (none in newly-introduced names) | — | — |

`create_llm_result` = verb + 2 words. All test names follow `test_*` pytest
convention and are out of scope.

## God-function findings

| file:line | name | lines | jobs_detected |
|---|---|---|---|
| services/llm/claude.py:43 | `analyze_and_generate` | ~100 (body roughly 75) | read inputs → create prompt → write snapshot → hash → call API → time → parse JSON → write breadcrumbs (≥4 jobs) | MAJOR |
| services/llm/gemini.py:43 | `analyze_and_generate` | ~125 (body roughly 90) | same shape as Claude, plus defensive usage_metadata extraction inline | MAJOR |

These were already long before the breadcrumb feature, but the diff makes
them visibly worse: timing setup, hashing, snapshot capture, and breadcrumb
dict assembly all now live in the same function. Recommended split:

- `read_prompt_text(profile, language, job_description)` → returns
  `(system_prompt, user_prompt, full_prompt_text)`.
- `read_profile_snapshot(profile)` → returns the stable JSON string.
- `parse_response_json(response_text)` → returns the parsed dict.
- `create_breadcrumbs(...)` → returns the breadcrumbs dict.
- `analyze_and_generate` orchestrates only.

The implementer should not refactor on this PR if scope-creep is a concern;
recording the violation is sufficient.

## Framework-suffix findings

| file_or_class | suffix | suggested_name |
|---|---|---|
| (no new structures introduced) | — | — |

Pre-existing in the repo, untouched by this feature, recorded only for
completeness: `services/llm/factory.py` (file), `ClaudeProvider`,
`GeminiProvider`, `_LazyLLMService`, `LLMProvider`, `ResumeGeneratorService`.
Not introduced by this diff.

## Comment violations

| file | non-header_comment_count (new) | sample_lines |
|---|---|---|
| database.py | 1 | `# LLM Call Breadcrumbs: per-call provenance for replay/grading` (around the ALTER TABLE block) |
| services/llm/claude.py | 0 new (docstring updated; counts as pre-existing docstring drift) | updated `Returns:` block |
| services/llm/gemini.py | 0 new (docstring updated) | updated `Returns:` block |
| services/llm/base.py | 0 new (docstring updated) | updated `Returns:` block |
| services/llm/__init__.py | 0 new (docstring updated) | updated `Returns:` block |
| services/resume_generator.py | 0 new (only blank lines / SQL additions) | — |
| tests/* | docstrings only (allowed per brief) | — |

Rule-5 read:
- The single new SQL-block comment in `database.py` (`# LLM Call Breadcrumbs:
  per-call provenance for replay/grading`) is a textbook "comment explaining
  what code does" — the surrounding `ALTER TABLE generated_resumes ADD COLUMN
  …` statements already say it. MINOR.
- The four docstring updates in production code (`base.py`, `claude.py`,
  `gemini.py`, `services/llm/__init__.py`) extend pre-existing docstrings.
  CLAUDE.md rule 5 is absolute ("After the header: ZERO comments. No inline
  comments. No docstrings."), but the docstrings already existed before this
  feature — this PR did not introduce them, it only updated content. Flagged
  as MINOR pre-existing drift made slightly worse.

## Abbreviation findings (rule 3)

| file:line | name | issue | suggested_name | severity |
|---|---|---|---|---|
| services/llm/claude.py:83 | `t0 = time.monotonic()` | abbreviation; reader must translate "t0 = time at zero" | `start_time` or `started_at` | MAJOR |
| services/llm/gemini.py:87 | `t0 = time.monotonic()` | same | `start_time` | MAJOR |
| tests/test_resumes.py:109 | `snap = json.loads(...)` | abbreviation of `snapshot` | `snapshot` | MAJOR |
| tests/test_resume_generator.py:354–355 | `r1`, `r2` | abbreviations | `first_response`, `second_response` | MAJOR |
| tests/test_database_migrations.py:36, 50, 55 | `cols`, `cols_first`, `cols_second` | abbreviation of `columns` | `columns`, `first_columns`, `second_columns` | MAJOR |

This is the single largest cluster of new lean-code drift. Rule 3 from
CLAUDE.md is unambiguous: "No abbreviations anywhere in names." It applies to
local variables, not only function names.

## Forbidden-pattern findings (rule 8 / table)

None new. `create_llm_result(**breadcrumb_overrides)` was examined for the
"shared helper with flags" pattern (rule 9). It does not switch behaviour by
flag — it merges overrides into a default dict and serves one scope (test
fixture for the tuple shape). PASS, listed in "Almost flagged" below.

## Almost flagged

Three weakest spots that I read closely and let pass:

1. **`create_llm_result(parsed, **breadcrumb_overrides)`** — The `**overrides`
   shape can look like rule 9 ("shared helper serves multiple scopes via a
   `context` / `mode` / boolean flag parameter"). It is not: every caller is
   in `tests/`, the helper's single job is "produce a `(parsed, breadcrumbs)`
   tuple with sentinel defaults", and overrides do not pick a different code
   path — they only swap field values. Borderline but PASS. If a future call
   starts passing a flag like `mode="error"` to flip the return type, that
   crosses the line.

2. **`analyze_and_generate` signature change (Protocol → tuple)** — the verb
   `analyze_and_generate` is not in the nine permitted verbs and is two verbs
   joined by `and` (the rule "no two verbs used for the same operation" is
   about cross-codebase consistency, not within a single name, but using two
   verbs in one identifier still hides what the function actually does).
   It is pre-existing across `base.py`, `claude.py`, `gemini.py`,
   `services/llm/__init__.py`, and `services/resume_generator.py`. This PR
   does not introduce it, so I did not flag it as new — but recording here
   for the next refactor pass: `read_resume_from_prompt` would be honest.

3. **Inline SQL strings in `services/resume_generator.py:88-114`** — the
   16-placeholder INSERT is verbose but not a lean-code violation per se.
   Could be split into `write_resume_record(conn, columns)` for clarity, but
   that risks being a "one-line extracted function" (rule 7) given there is
   one caller. PASS.

## Final verdict

**ISSUES.**

Major findings to address before this feature is considered lean-clean:

1. Two test helpers use disallowed verbs (`_count_resume_rows`,
   `capture_and_return`). Rename per the table above.
2. Five new abbreviated local-variable names (`t0` × 2, `snap`, `r1`/`r2`,
   `cols`/`cols_first`/`cols_second`). Rule 3 is unconditional.
3. The two provider `analyze_and_generate` methods cross the god-function
   threshold more clearly after this diff. At minimum, snapshot capture and
   breadcrumbs assembly should split out (`read_profile_snapshot`,
   `create_breadcrumbs`).
4. One new inline comment in `database.py` near the ALTER TABLE block.
   Remove it — the column names self-document.

Minor:
- Docstring updates on already-existing docstrings in `base.py`,
  `claude.py`, `gemini.py`, `services/llm/__init__.py` extend pre-existing
  rule-5 drift. Not introduced here, but the opportunity to delete those
  docstrings (and let the verb-correct function names speak) was missed.
