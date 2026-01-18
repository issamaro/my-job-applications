"""LLM service package.

This package provides an abstraction layer for LLM providers (Claude, Gemini).
The provider is selected via the LLM_PROVIDER environment variable.

Usage:
    from services.llm import llm_service

    result = await llm_service.analyze_and_generate(job_description, profile)
"""

from .base import LLMProvider
from .factory import get_provider

__all__ = ["llm_service", "get_provider", "LLMProvider"]


class _LazyLLMService:
    """Lazy-loading wrapper for the LLM service singleton.

    This defers provider initialization until first use, allowing
    the application to start without requiring API keys immediately.
    """

    _instance: LLMProvider | None = None

    def _get_instance(self) -> LLMProvider:
        if self._instance is None:
            self._instance = get_provider()
        return self._instance

    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict,
        language: str = "en",
    ) -> dict:
        """Delegate to the underlying provider."""
        return await self._get_instance().analyze_and_generate(
            job_description, profile, language
        )


# Global singleton - lazily initialized on first use
llm_service = _LazyLLMService()
