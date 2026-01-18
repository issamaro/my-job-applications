"""Gemini LLM provider implementation."""

import os
import json
import logging
from google import genai
from google.genai import types, errors

from .base import (
    LANGUAGE_INSTRUCTIONS,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _get_model() -> str:
    """Get the Gemini model name from environment or default."""
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


class GeminiProvider:
    """Gemini LLM provider using Google's GenAI API."""

    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict,
        language: str = "en",
    ) -> dict:
        """Generate resume analysis and content using Gemini.

        Args:
            job_description: The job posting text to analyze
            profile: Candidate profile dictionary
            language: Output language code (en, fr, nl)

        Returns:
            Dictionary containing job_title, company_name, match_score,
            job_analysis, and resume content

        Raises:
            ConnectionError: When API connection fails
            RuntimeError: When API returns an error or rate limit
            ValueError: When response cannot be parsed as JSON
        """
        client = _get_client()
        model = _get_model()

        profile_json = json.dumps(profile, indent=2)
        language_instruction = LANGUAGE_INSTRUCTIONS.get(
            language, LANGUAGE_INSTRUCTIONS["en"]
        )
        user_prompt = USER_PROMPT_TEMPLATE.format(
            job_description=job_description,
            profile_json=profile_json,
            language_instruction=language_instruction,
        )

        # Combine system prompt and user prompt for Gemini
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            response_text = response.text

            # Parse JSON from response
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

            return result

        except errors.APIError as e:
            logger.error(f"Gemini API error: {e.code} - {e.message}")

            if e.code == 401:
                raise ValueError("Invalid GEMINI_API_KEY")
            elif e.code == 404:
                raise ValueError(f"Model not found: {model}")
            elif e.code == 429:
                raise RuntimeError("AI service is busy, please try again later")
            else:
                raise RuntimeError(f"AI service error: {e.code} - {e.message}")

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
            # Handle connection errors
            if "connect" in str(e).lower() or "network" in str(e).lower():
                logger.error(f"Connection error: {e}")
                raise ConnectionError(f"Could not connect to AI service: {e}")
            logger.error(f"Unexpected error in Gemini provider: {type(e).__name__}: {e}")
            raise
