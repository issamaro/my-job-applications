# Reproduce-first — llm-call-breadcrumbs

**Not applicable.** This slice is greenfield instrumentation, not a bug fix. The
`generated_resumes` table currently has no breadcrumb columns — there is no
"failure" to reproduce, only a missing capability. Confirmed by inspecting
`database.py:339-353` (table DDL) and `database.py:357-376` (ALTER TABLE list):
none of `prompt_path`, `prompt_hash`, `provider`, `model`, `profile_snapshot`,
`raw_output`, `latency_ms`, `input_tokens`, `output_tokens` exist today.

The success criteria in FEATURE_SPEC fully replace a repro file.
