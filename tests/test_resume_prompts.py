"""Assertions over the resume-generation prompt strings.

Guards two contracts the prompts encode:
  * a 350-character hard cap on summary and per-experience descriptions
  * a banned third-person voice in the summary
"""

from services.llm.base import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def test_system_prompt_states_summary_length_cap():
    assert "350 characters" in SYSTEM_PROMPT
    assert "resume.summary" in SYSTEM_PROMPT


def test_system_prompt_states_description_length_cap():
    assert "work_experiences[*].description" in SYSTEM_PROMPT
    assert "350" in SYSTEM_PROMPT


def test_system_prompt_forbids_third_person_summary_voice():
    lowered = SYSTEM_PROMPT.lower()
    assert "first person" in lowered
    assert ("third person" in lowered) or ("third-person" in lowered)
    assert "candidate's first or last name" in SYSTEM_PROMPT


def test_user_prompt_repeats_length_cap():
    assert "350 characters or fewer" in USER_PROMPT_TEMPLATE


def test_user_prompt_repeats_voice_rule():
    lowered = USER_PROMPT_TEMPLATE.lower()
    assert "first person" in lowered
    assert "third person" in lowered or "third-person" in lowered
