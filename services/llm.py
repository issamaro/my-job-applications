import os
import json
import logging
import anthropic
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


LANGUAGE_INSTRUCTIONS = {
    "en": "Generate all resume content in English.",
    "fr": "Generate all resume content in French (Français). Write the summary and work experience descriptions in French.",
    "nl": "Generate all resume content in Dutch (Nederlands). Write the summary and work experience descriptions in Dutch.",
}

SYSTEM_PROMPT = """You are an expert resume writer and career coach. Your task is to analyze
a job description and a candidate's profile, then create a tailored resume
that highlights the most relevant qualifications.

You must return valid JSON matching the specified schema.

Guidelines:
- Extract key requirements from the job description
- Match candidate qualifications to job requirements
- Reorder work experiences by relevance (most relevant first)
- Enhance descriptions to emphasize matching skills (but never fabricate)
- Calculate a realistic match score (0-100) based on requirement coverage
- Be honest about gaps - don't claim matches that don't exist"""

USER_PROMPT_TEMPLATE = """Analyze this job description and create a tailored resume from the candidate profile.

## LANGUAGE INSTRUCTION
{language_instruction}

## JOB DESCRIPTION
{job_description}

## CANDIDATE PROFILE
{profile_json}

## REQUIRED OUTPUT FORMAT
Return a JSON object with exactly this structure:
{{
  "job_title": "extracted job title",
  "company_name": "extracted company name or null",
  "match_score": 75.5,
  "job_analysis": {{
    "required_skills": [
      {{"name": "Python", "matched": true}},
      {{"name": "AWS", "matched": false}}
    ],
    "preferred_skills": [
      {{"name": "Kubernetes", "matched": false}}
    ],
    "experience_years": {{"required": 5, "matched": true}},
    "education": {{"required": "Bachelor's CS", "matched": true}}
  }},
  "resume": {{
    "summary": "A tailored professional summary...",
    "work_experiences": [
      {{
        "id": 1,
        "company": "Acme Corp",
        "title": "Senior Developer",
        "start_date": "2020-01",
        "end_date": null,
        "description": "Tailored description emphasizing relevant skills...",
        "match_reasons": ["Python", "Team Leadership"],
        "included": true,
        "order": 1
      }}
    ],
    "skills": [
      {{"name": "Python", "matched": true, "included": true}}
    ],
    "education": [
      {{
        "id": 1,
        "institution": "State University",
        "degree": "BS Computer Science",
        "field_of_study": "Computer Science",
        "graduation_year": 2017,
        "included": true
      }}
    ],
    "projects": [
      {{
        "id": 1,
        "name": "Project Name",
        "description": "Project description",
        "technologies": "Python, Docker",
        "included": false
      }}
    ]
  }}
}}

Important:
- Only include profile items that are relevant to this job
- Reorder work experiences by relevance (most relevant first)
- For each included work experience, explain why it matches (match_reasons)
- Be accurate with the match_score - it should reflect actual qualification coverage
- Keep the original IDs from the profile for work_experiences, education, and projects
- Set included=false for items that are not relevant"""


class LLMService:
    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict,
        language: str = "en",
    ) -> dict:
        client = get_client()

        profile_json = json.dumps(profile, indent=2)
        language_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])
        user_prompt = USER_PROMPT_TEMPLATE.format(
            job_description=job_description,
            profile_json=profile_json,
            language_instruction=language_instruction,
        )

        try:
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            response_text = message.content[0].text

            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)

            return result

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
            logger.error(f"Response text (last 500 chars): {response_text[-500:] if response_text else 'None'}")
            # Log truncation hint if response seems cut off
            if response_text and not response_text.rstrip().endswith("}"):
                raise ValueError("AI response was truncated. Try a shorter job description.")
            raise ValueError(f"Invalid response from AI service: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {type(e).__name__}: {e}")
            raise


llm_service = LLMService()
