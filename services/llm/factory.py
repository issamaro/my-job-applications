"""LLM provider factory.

This module provides factory functions for creating LLM provider instances
based on environment configuration.
"""

import os
import logging

from .base import LLMProvider
from .claude import ClaudeProvider
from .gemini import GeminiProvider

logger = logging.getLogger(__name__)

VALID_PROVIDERS = {"claude", "gemini"}


def get_provider(provider_name: str | None = None) -> LLMProvider:
    """Get an LLM provider instance based on configuration.

    Args:
        provider_name: Optional explicit provider name. If not provided,
                      reads from LLM_PROVIDER env var (default: "claude")

    Returns:
        An LLM provider instance implementing the LLMProvider protocol

    Raises:
        ValueError: If provider name is invalid or required API key is missing
    """
    if provider_name is None:
        provider_name = os.environ.get("LLM_PROVIDER", "claude")

    provider_name = provider_name.lower()

    if provider_name not in VALID_PROVIDERS:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {provider_name}. "
            f"Valid options: {', '.join(sorted(VALID_PROVIDERS))}"
        )

    logger.info(f"Using LLM provider: {provider_name}")

    if provider_name == "claude":
        return ClaudeProvider()
    elif provider_name == "gemini":
        return GeminiProvider()

    # Should never reach here due to validation above
    raise ValueError(f"Unknown provider: {provider_name}")
