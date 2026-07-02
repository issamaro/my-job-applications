"""Tests for the LLM provider factory."""

import pytest

import settings
from services.llm.factory import get_provider, VALID_PROVIDERS
from services.llm.claude import ClaudeProvider
from services.llm.gemini import GeminiProvider


class TestGetProvider:
    """Tests for get_provider factory function."""

    def test_default_provider_is_claude(self, monkeypatch):
        """Test that the default provider is Claude (the documented default)."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "claude")
        assert isinstance(get_provider(), ClaudeProvider)

    def test_explicit_claude_provider(self, monkeypatch):
        """Test explicit selection of Claude provider."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "claude")
        assert isinstance(get_provider(), ClaudeProvider)

    def test_explicit_gemini_provider(self, monkeypatch):
        """Test explicit selection of Gemini provider."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
        assert isinstance(get_provider(), GeminiProvider)

    def test_provider_name_case_insensitive(self, monkeypatch):
        """Test that provider name is case-insensitive."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "CLAUDE")
        assert isinstance(get_provider(), ClaudeProvider)

    def test_invalid_provider_raises_error(self):
        """Test that invalid provider name raises ValueError with valid options."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider")

        error_msg = str(exc_info.value)
        assert "Invalid LLM_PROVIDER" in error_msg
        assert "invalid_provider" in error_msg
        for provider in VALID_PROVIDERS:
            assert provider in error_msg

    def test_missing_claude_api_key_raises_error(self, monkeypatch):
        """Test that an empty ANTHROPIC_API_KEY raises ValueError."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "claude")
        monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")

        import services.llm.claude as claude_module
        claude_module._client = None

        provider = get_provider()

        with pytest.raises(ValueError) as exc_info:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                provider.analyze_and_generate("test", {})
            )

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_missing_gemini_api_key_raises_error(self, monkeypatch):
        """Test that an empty GEMINI_API_KEY raises ValueError."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

        import services.llm.gemini as gemini_module
        gemini_module._client = None

        provider = get_provider()

        with pytest.raises(ValueError) as exc_info:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                provider.analyze_and_generate("test", {})
            )

        assert "GEMINI_API_KEY" in str(exc_info.value)

    def test_explicit_provider_name_overrides_env(self, monkeypatch):
        """Test that explicit provider_name argument overrides settings."""
        monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
        provider = get_provider("claude")
        assert isinstance(provider, ClaudeProvider)
