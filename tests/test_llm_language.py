"""Tests for LLM language support."""

import pytest
from services.llm.base import LANGUAGE_INSTRUCTIONS, USER_PROMPT_TEMPLATE


class TestLanguageInstructions:
    """Tests for language instructions."""

    def test_english_instruction_exists(self):
        """English language instruction should exist."""
        assert "en" in LANGUAGE_INSTRUCTIONS
        assert "English" in LANGUAGE_INSTRUCTIONS["en"]

    def test_french_instruction_exists(self):
        """French language instruction should exist."""
        assert "fr" in LANGUAGE_INSTRUCTIONS
        assert "French" in LANGUAGE_INSTRUCTIONS["fr"]
        assert "Français" in LANGUAGE_INSTRUCTIONS["fr"]

    def test_dutch_instruction_exists(self):
        """Dutch language instruction should exist."""
        assert "nl" in LANGUAGE_INSTRUCTIONS
        assert "Dutch" in LANGUAGE_INSTRUCTIONS["nl"]
        assert "Nederlands" in LANGUAGE_INSTRUCTIONS["nl"]


class TestUserPromptTemplate:
    """Tests for user prompt template."""

    def test_prompt_has_language_instruction_placeholder(self):
        """Prompt template should include language instruction placeholder."""
        assert "{language_instruction}" in USER_PROMPT_TEMPLATE

    def test_prompt_has_job_description_placeholder(self):
        """Prompt template should include job description placeholder."""
        assert "{job_description}" in USER_PROMPT_TEMPLATE

    def test_prompt_has_profile_json_placeholder(self):
        """Prompt template should include profile JSON placeholder."""
        assert "{profile_json}" in USER_PROMPT_TEMPLATE

    def test_prompt_can_format_with_all_placeholders(self):
        """Prompt template should format correctly with all placeholders."""
        formatted = USER_PROMPT_TEMPLATE.format(
            language_instruction="Generate in English",
            job_description="Test job description",
            profile_json='{"name": "Test"}'
        )
        assert "Generate in English" in formatted
        assert "Test job description" in formatted
        assert '{"name": "Test"}' in formatted
