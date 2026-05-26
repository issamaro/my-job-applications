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
    ) -> tuple[dict, dict]:
        """Generate resume analysis and content from job description and profile.

        Args:
            job_description: The job posting text to analyze
            profile: Candidate profile dictionary
            language: Output language code (en, fr, nl)

        Returns:
            A two-element tuple (parsed, breadcrumbs):
            - parsed: dict with job_title, company_name, match_score,
              job_analysis, and resume content.
            - breadcrumbs: dict with the 9 provider-owned fields:
              provider, model, prompt_path, prompt_hash, raw_output,
              latency_ms, input_tokens, output_tokens, profile_snapshot.
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
- Enhance descriptions to emphasize matching skills (but never fabricate)
- Calculate a realistic match score (0-100) based on requirement coverage
- Be honest about gaps - don't claim matches that don't exist

Length limits (hard caps, do not exceed):
- `resume.summary`: at most 350 characters total. Aim for 2-3 tight sentences.
- Each `resume.work_experiences[*].description`: at most 350 characters. One focused paragraph, no bullet lists.
- Cut filler ("responsible for", "tasked with", "in charge of"). Lead with the strongest verb and the highest-impact result.

Voice for `resume.summary` (strict):
- Write the summary in FIRST PERSON ("I led...", "I built...") OR ACTION-LED with no pronoun ("Led teams across...", "Built the platform that...").
- NEVER use the candidate's first or last name as the subject of a sentence in the summary. Forbidden patterns include "{First} {Last} is...", "{First} {Last} has...", "{First} leads...", and any other third-person construction that names the candidate.
- The summary must read as the candidate speaking, not as someone describing the candidate."""

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
- Only include profile skills, education, and projects that are relevant to this job. ALL work_experiences are always included — see the work-experiences rule below.
- For each work experience, populate match_reasons when there is overlap with the job; an empty array is acceptable when there is no overlap.
- Be accurate with the match_score - it should reflect actual qualification coverage
- Keep the original IDs from the profile for work_experiences, education, and projects
- Set included=false for skills, education, or projects that are not relevant. NEVER set included=false on a work_experience.
- WORK EXPERIENCES — return ALL profile work_experiences, every one with included=true. Do not drop any. Do not set included=false on any work experience under any circumstance. Tailor descriptions and provide match_reasons regardless of relevance. The user toggles inclusion in the UI, not the LLM.
- HARD LIMIT: `resume.summary` and every `resume.work_experiences[*].description` must be 350 characters or fewer. Count characters before returning. If a draft exceeds the cap, rewrite it tighter — do not return overflow.
- VOICE: write `resume.summary` in first person ("I ...") or action-led with no pronoun ("Led ...", "Built ..."). Do NOT begin with the candidate's name or refer to the candidate in the third person anywhere in the summary."""
