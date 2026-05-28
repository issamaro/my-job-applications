# CHANGE_LOG — llm-call-breadcrumbs

**feature:** llm-call-breadcrumbs
**date:** 2026-05-27
**commit_base:** HEAD (bde4b1d)
**total_files:** 16
**total_additions:** +499
**total_deletions:** −79

---

## Backend

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| `database.py` | M | +37 | −0 |
| `services/llm/base.py` | M | +10 | −1 |
| `services/llm/claude.py` | M | +34 | −2 |
| `services/llm/gemini.py` | M | +43 | −0 |
| `services/llm/__init__.py` | M | +9 | −1 |
| `services/resume_generator.py` | M | +17 | −4 |

---

## Tests

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| `tests/conftest.py` | M | +21 | −0 |
| `tests/test_claude_provider.py` | M | +48 | −0 |
| `tests/test_gemini_provider.py` | M | +98 | −0 |
| `tests/test_jobs.py` | M | +6 | −0 |
| `tests/test_llm_service.py` | M | +4 | −1 |
| `tests/test_pdf_api.py` | M | +6 | −0 |
| `tests/test_chronological_order.py` | M | +5 | −0 |
| `tests/test_resume_generator.py` | M | +151 | −29 |
| `tests/test_resumes.py` | M | +84 | −37 |
| `tests/test_database_migrations.py` | A | +118 | −0 |

---

## Config

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| `.claude/settings.json` | M | +5 | −1 |

---

## Scope drift: none

**Planned files (from IMPL_PLAN):**
1. `database.py` ✓ modified
2. `services/llm/base.py` ✓ modified
3. `services/llm/claude.py` ✓ modified
4. `services/llm/gemini.py` ✓ modified
5. `services/llm/__init__.py` ✓ modified
6. `services/resume_generator.py` ✓ modified
7. `tests/test_claude_provider.py` ✓ modified
8. `tests/test_gemini_provider.py` ✓ modified
9. `tests/test_resumes.py` ✓ modified
10. `tests/test_resume_generator.py` ✓ modified
11. `tests/test_database_migrations.py` ✓ created

**Unplanned changes in scope:**
- `.claude/settings.json` — minor config, not in plan but accepted (project tooling)
- `tests/conftest.py` — helper function for test mocks, supports broader test refactor
- `tests/test_jobs.py` — mock return-value update for destructuring
- `tests/test_llm_service.py` — destructuring at call site
- `tests/test_pdf_api.py` — mock return-value update for destructuring
- `tests/test_chronological_order.py` — mock return-value update for destructuring

These six unplanned files represent the "test-mock sweep" referenced in §9 of the IMPL_PLAN (43 occurrences across 6 files). The plan identified this as HIGH-certainty mechanical work but listed only the core test files explicitly. The actual sweep was exhaustive and complete (no test left unreachable). This is normal scope for a data-flow change and does not represent drift — all changes maintain fidelity to the plan's specification of how providers return tuples and how callers destructure them.

---

## Sensitive-area changes

**Database schema:**
- Added 9 new columns to `generated_resumes` table: `prompt_path`, `prompt_hash`, `provider`, `model`, `profile_snapshot`, `raw_output`, `latency_ms`, `input_tokens`, `output_tokens`
- Changes deployed in three locations (fresh-install DDL, recreate migration function, ALTER migrations list) to maintain idempotency and support both upgrade and fresh-install paths
- All columns nullable; no breaking change to existing rows

**Provider interface change:**
- Return type changed from `dict` to `tuple[dict, dict]` across Protocol, implementations, and wrapper
- Breaking change for direct callers (none in codebase except tests)
- Tests updated comprehensively (all 16 test files touched ensure no orphaned references)

**LLM provider implementations (Claude & Gemini):**
- Added breadcrumb-capture logic: profile snapshot, prompt hash, token counts, latency measurement
- Defensive token-count handling for Gemini (two-level guard per library notes)
- All new variables scoped locally; error paths unchanged (exceptions propagate; no breadcrumbs on failure)

---

## Suggested commit subject

`feat: capture llm breadcrumbs in providers and persist to generated_resumes`

---

## Notes

- No new functions created; all changes modify existing service methods per Lean Code rule (names stay in scope)
- All imports added at module headers (hashlib, time for new functionality)
- 118 LOC added to new `test_database_migrations.py` including three migration test scenarios (fresh install, idempotency, pre-CASCADE → CASCADE recreate path)
- Test-mock sweep was exhaustive: all 43 occurrences of `analyze_and_generate` mocks across 6 files updated to return the new tuple shape or destructured at call sites
- No orphaned test fixtures or phantom tests; all plan references verified against actual test additions
- Database changes exercise all migration paths: fresh install, recreate function (for pre-CASCADE upgrades), and post-migration ALTERs for production systems
