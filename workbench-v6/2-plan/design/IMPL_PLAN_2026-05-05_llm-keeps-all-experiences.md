# IMPL_PLAN — llm-keeps-all-experiences

date: 2026-05-05
ceremony_level: S
slug: llm-keeps-all-experiences
revision: 2 (post-review — Path A: prompt only)

## Goal

Tell the LLM to return every work experience with `included=true`. The user — not the LLM — decides which experiences appear in the final CV. Skills, education, and projects keep their current LLM-driven inclusion logic.

## Approach (Path A — prompt only)

The refined backlog's "Scope IN bullet 3" — "adjust downstream code that depends on the LLM picking inclusion" — is N/A in practice: no downstream code currently makes inclusion decisions for work experiences (`pdf_generator.py` already defaults `included` to `True`, `resume_generator.py` passes through whatever the LLM returns). So the only change needed is in the prompt.

This matches how every other prompt rule is enforced (length cap, voice rule, id retention): the LLM is instructed and trusted; tests assert the prompt encodes the rule.

## Libraries

No new libraries. No parallel research dispatch.

## Files touched

### Modify — `services/llm/base.py` (USER_PROMPT_TEMPLATE)

Edit the `Important:` block of `USER_PROMPT_TEMPLATE`. Concrete edits:

1. Replace the line `Only include profile items that are relevant to this job` with:
   `Only include profile skills, education, and projects that are relevant to this job. ALL work_experiences are always included — see the work-experiences rule below.`

2. Replace the line `For each included work experience, explain why it matches (match_reasons)` with:
   `For each work experience, populate match_reasons when there is overlap with the job; an empty array is acceptable when there is no overlap.`

3. Replace the line `Set included=false for items that are not relevant` with:
   `Set included=false for skills, education, or projects that are not relevant. NEVER set included=false on a work_experience.`

4. Add a new explicit rule at the end of the `Important:` block (before the HARD LIMIT line):
   `WORK EXPERIENCES — return ALL profile work_experiences, every one with included=true. Do not drop any. Do not set included=false on any work experience under any circumstance. Tailor descriptions and provide match_reasons regardless of relevance. The user toggles inclusion in the UI, not the LLM.`

`SYSTEM_PROMPT` does not need a change — the rule lives in the user prompt where the schema is defined.

### Modify — `tests/test_resume_prompts.py`

Add three assertions that pin the rule into the prompt text:

- `test_user_prompt_requires_all_work_experiences_included` — assert that `USER_PROMPT_TEMPLATE` contains the substring `return ALL profile work_experiences` AND `included=true`. Both substrings must be present (no proximity claim).
- `test_user_prompt_forbids_setting_included_false_on_work_experience` — assert that `USER_PROMPT_TEMPLATE` contains `NEVER set included=false on a work_experience`.
- `test_user_prompt_allows_empty_match_reasons` — assert that `USER_PROMPT_TEMPLATE` contains the phrase `empty array is acceptable` (or equivalent text from rule edit #2). This pins BDD scenario 2 (irrelevant experience → empty `match_reasons` is allowed).

These assertions cover both BDD scenarios from the refined backlog. No integration test through the API is needed — the contract is "the prompt instructs the LLM correctly," same trust model as the existing length-cap and voice-rule tests.

## Out of scope (this revision)

- No change to `services/resume_generator.py` (no post-LLM guard).
- No change to existing integration tests in `tests/test_resume_generator.py` — none of them depend on the inclusion behavior of work experiences.
- No UI changes.
- No change to skills / education / projects inclusion logic.
- No change to `match_score` or `job_analysis`.

## Risks

- **LLM disobedience** — if the LLM ignores the new rule and sets `included=false` on an experience, that experience disappears from the editor. Failure mode is **visible** to the user. Same trust model as length cap and voice rule. Acceptable.
- **Prompt-text proximity** — the prompt assertions use substring checks, not proximity. If a future edit splits the rule across paragraphs, the assertions still pass. This is intentional — proximity checks are flaky. The rule's coherence is verified by reading the prompt, not by tests.

## Test plan

Automated:
- New: 3 assertions in `tests/test_resume_prompts.py`.
- Regression: existing prompt tests, generator tests, chronological-order tests must still pass without changes.

Manual (inspect phase):
- Run real tailored-resume generation against a profile with 3+ work experiences and a job description that matches only one. Verify all experiences appear in the editor with their checkboxes; verify the user can toggle them.

## Lean-code compliance

No new functions added. Only string-edit operations on the existing prompt template. No naming concerns.
