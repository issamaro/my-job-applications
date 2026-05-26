"""Claude LLM provider implementation."""

import hashlib
import json
import logging
import os
import time

import anthropic
from anthropic import AsyncAnthropic

from .base import (
    LANGUAGE_INSTRUCTIONS,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    """Get or create the Anthropic async client singleton."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


def _get_model() -> str:
    """Get the Claude model name from environment or default."""
    return os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")


class ClaudeProvider:
    """Claude LLM provider using Anthropic's API."""

    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict,
        language: str = "en",
    ) -> tuple[dict, dict]:
        """Generate resume analysis and content using Claude.

        Args:
            job_description: The job posting text to analyze
            profile: Candidate profile dictionary
            language: Output language code (en, fr, nl)

        Returns:
            A tuple (parsed, breadcrumbs). parsed is the resume dict. breadcrumbs
            carries provider, model, prompt_path, prompt_hash, raw_output,
            latency_ms, input_tokens, output_tokens, profile_snapshot.

        Raises:
            ConnectionError: When API connection fails
            RuntimeError: When API returns an error or rate limit
            ValueError: When response cannot be parsed as JSON
        """
        client = _get_client()

        profile_json = json.dumps(profile, indent=2)
        language_instruction = LANGUAGE_INSTRUCTIONS.get(
            language, LANGUAGE_INSTRUCTIONS["en"]
        )
        user_prompt = USER_PROMPT_TEMPLATE.format(
            job_description=job_description,
            profile_json=profile_json,
            language_instruction=language_instruction,
        )

        profile_snapshot = json.dumps(profile, sort_keys=True, ensure_ascii=False)
        prompt_text = SYSTEM_PROMPT + "\n\n" + user_prompt
        prompt_hash = hashlib.sha1(prompt_text.encode("utf-8")).hexdigest()
        model_id = _get_model()

        start_time = time.monotonic()
        try:
            message = await client.messages.create(
                model=model_id,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            latency_ms = int((time.monotonic() - start_time) * 1000)

            response_text = message.content[0].text

            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start == -1:
                raise ValueError("No JSON found in response")
            if json_end == 0:
                # Has opening brace but no closing brace - truncated
                raise ValueError(
                    "AI response was truncated. Try a shorter job description."
                )

            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)

            breadcrumbs = {
                "provider": "claude",
                "model": model_id,
                "prompt_path": "services/llm/base.py:SYSTEM_PROMPT",
                "prompt_hash": prompt_hash,
                "raw_output": response_text,
                "latency_ms": latency_ms,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "profile_snapshot": profile_snapshot,
            }
            return result, breadcrumbs

        except anthropic.APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            raise ConnectionError(f"Could not connect to AI service: {e}")
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            raise RuntimeError("AI service is busy, please try again later")
        except anthropic.APIStatusError as e:
            logger.error(f"API status error: {e.status_code} - {e.message}")
            raise RuntimeError(f"AI service error: {e.status_code} - {e.message}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(
                f"Response text (last 500 chars): {response_text[-500:] if response_text else 'None'}"
            )
            if response_text and not response_text.rstrip().endswith("}"):
                raise ValueError(
                    "AI response was truncated. Try a shorter job description."
                )
            raise ValueError(f"Invalid response from AI service: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Claude provider: {type(e).__name__}: {e}")
            raise
