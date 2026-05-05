feature: llm-keeps-all-experiences
date: 2026-05-05
revision: 2 (Path A — prompt only)
total_checkboxes: 12
derived_from: IMPL_PLAN_2026-05-05_llm-keeps-all-experiences.md (rev 2), llm-keeps-all-experiences.md (refined backlog)

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = 3.13  (verify: `cat .python-version`)
- [ ] `pyproject.toml` declares `requires-python = ">=3.13"`  (verify: `grep requires-python pyproject.toml`)
- [ ] Virtual environment activated  (verify: `python --version` matches 3.13.x)

---

## Section 1 — Dependencies

n/a — no new libraries.

---

## Section 2 — Syntax

### `services/llm/base.py` (USER_PROMPT_TEMPLATE)

- [ ] The `Important:` block contains a new explicit rule line: `WORK EXPERIENCES — return ALL profile work_experiences, every one with included=true.`  (verify: `grep -n "return ALL profile work_experiences" services/llm/base.py`)
- [ ] The `Important:` block contains: `NEVER set included=false on a work_experience`  (verify: `grep -n "NEVER set included=false on a work_experience" services/llm/base.py`)
- [ ] The `Important:` block contains: `empty array is acceptable` (governing match_reasons for irrelevant experiences)  (verify: `grep -n "empty array is acceptable" services/llm/base.py`)
- [ ] The `Important:` block scopes the `Only include profile items` rule to skills, education, and projects (NOT work experiences)  (verify: read the line; confirm "skills, education, and projects" appears in that rule)
- [ ] `SYSTEM_PROMPT` block is unchanged  (verify: `git diff services/llm/base.py` shows no edits inside the SYSTEM_PROMPT triple-quoted string)

---

## Section 3 — UX

n/a — no UX_DESIGN.

---

## Section 4 — Tests

### `tests/test_resume_prompts.py` — three new tests

- [ ] `test_user_prompt_requires_all_work_experiences_included` exists  (verify: `grep -n "def test_user_prompt_requires_all_work_experiences_included" tests/test_resume_prompts.py`)
- [ ] That test asserts both substrings are present: `return ALL profile work_experiences` AND `included=true`  (verify: read the assertion body)
- [ ] `test_user_prompt_forbids_setting_included_false_on_work_experience` exists and asserts `NEVER set included=false on a work_experience` is in `USER_PROMPT_TEMPLATE`  (verify: `grep -n "def test_user_prompt_forbids_setting_included_false_on_work_experience" tests/test_resume_prompts.py`)
- [ ] `test_user_prompt_allows_empty_match_reasons` exists and asserts `empty array is acceptable` is in `USER_PROMPT_TEMPLATE`  (verify: `grep -n "def test_user_prompt_allows_empty_match_reasons" tests/test_resume_prompts.py`)

### Regression gate

- [ ] All pre-existing tests still pass  (verify: `pytest tests/test_resume_prompts.py tests/test_resume_generator.py tests/test_resumes.py tests/test_chronological_order.py -v`)

---

## Section 5 — Accessibility

n/a — no UX changes.

---

## Section 6 — Project-specific

n/a — no project-checks.md present.
