"""Tests for the LLM provider factory."""

import pytest
from unittest.mock import patch

from services.llm.factory import get_provider, VALID_PROVIDERS
from services.llm.claude import ClaudeProvider
from services.llm.gemini import GeminiProvider


class TestGetProvider:
    """Tests for get_provider factory function."""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    def test_default_provider_is_claude(self):
        """Test that default provider is Claude when no LLM_PROVIDER is set."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove LLM_PROVIDER if it exists
            import os
            os.environ.pop("LLM_PROVIDER", None)

            provider = get_provider()
            assert isinstance(provider, ClaudeProvider)

    @patch.dict("os.environ", {"LLM_PROVIDER": "claude", "ANTHROPIC_API_KEY": "test-key"})
    def test_explicit_claude_provider(self):
        """Test explicit selection of Claude provider."""
        provider = get_provider()
        assert isinstance(provider, ClaudeProvider)

    @patch.dict("os.environ", {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"})
    def test_explicit_gemini_provider(self):
        """Test explicit selection of Gemini provider."""
        provider = get_provider()
        assert isinstance(provider, GeminiProvider)

    @patch.dict("os.environ", {"LLM_PROVIDER": "CLAUDE", "ANTHROPIC_API_KEY": "test-key"})
    def test_provider_name_case_insensitive(self):
        """Test that provider name is case-insensitive."""
        provider = get_provider()
        assert isinstance(provider, ClaudeProvider)

    def test_invalid_provider_raises_error(self):
        """Test that invalid provider name raises ValueError with valid options."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider")

        error_msg = str(exc_info.value)
        assert "Invalid LLM_PROVIDER" in error_msg
        assert "invalid_provider" in error_msg
        # Verify valid options are listed
        for provider in VALID_PROVIDERS:
            assert provider in error_msg

    @patch.dict("os.environ", {"LLM_PROVIDER": "claude"}, clear=True)
    def test_missing_claude_api_key_raises_error(self):
        """Test that missing ANTHROPIC_API_KEY raises ValueError."""
        # Reset the client singleton to force re-initialization
        import services.llm.claude as claude_module
        claude_module._client = None

        provider = get_provider()

        with pytest.raises(ValueError) as exc_info:
            # The error happens when the provider tries to get the client
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                provider.analyze_and_generate("test", {})
            )

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    @patch.dict("os.environ", {"LLM_PROVIDER": "gemini"}, clear=True)
    def test_missing_gemini_api_key_raises_error(self):
        """Test that missing GEMINI_API_KEY raises ValueError."""
        # Reset the client singleton to force re-initialization
        import services.llm.gemini as gemini_module
        gemini_module._client = None

        provider = get_provider()

        with pytest.raises(ValueError) as exc_info:
            # The error happens when the provider tries to get the client
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                provider.analyze_and_generate("test", {})
            )

        assert "GEMINI_API_KEY" in str(exc_info.value)

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_explicit_provider_name_overrides_env(self):
        """Test that explicit provider_name argument overrides env var."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "gemini"}):
            provider = get_provider("claude")
            assert isinstance(provider, ClaudeProvider)
