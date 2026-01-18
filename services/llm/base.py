"""LLM Provider abstraction layer.

This module defines the protocol for LLM providers and shared constants
used across all provider implementations.
"""

from typing import Protocol


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""

    async def analyze_and_generate(
        self,
        job_description: str,
        profile: dict,
        language: str = "en",
    ) -> dict:
        """Generate resume analysis and content from job description and profile.

        Args:
            job_description: The job posting text to analyze
            profile: Candidate profile dictionary
            language: Output language code (en, fr, nl)

        Returns:
            Dictionary containing job_title, company_name, match_score,
            job_analysis, and resume content
        """
        ...


# Language instructions shared across all providers
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
