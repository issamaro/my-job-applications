"""Tests for chronological work-experience ordering."""

from unittest.mock import patch

from services.llm.base import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from tests.conftest import create_llm_result


def _create_minimal_profile(client):
    client.put(
        "/api/users",
        json={"full_name": "Jane Doe", "email": "jane@example.com"},
    )
    client.post(
        "/api/work-experiences",
        json={
            "company": "Anchor Corp",
            "title": "Engineer",
            "start_date": "2020-01",
            "description": "Anchor entry so profile passes the has_work_experience check.",
        },
    )
    client.post("/api/skills", json={"names": "Python"})
    client.post(
        "/api/education",
        json={
            "institution": "State University",
            "degree": "BS",
            "field_of_study": "Computer Science",
            "graduation_year": 2017,
        },
    )


def _build_llm_result(work_experiences):
    return create_llm_result({
        "job_title": "Software Engineer",
        "company_name": "TestCorp",
        "match_score": 80,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test summary",
            "work_experiences": work_experiences,
            "skills": [],
            "education": [],
            "projects": [],
        },
    })


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_sorts_work_experiences_chronological(mock_llm, client):
    _create_minimal_profile(client)

    mock_llm.return_value = _build_llm_result([
        {"id": 1, "company": "A", "title": "Junior Dev", "start_date": "2020-01", "end_date": "2022-02", "description": "", "match_reasons": [], "included": True, "order": 0},
        {"id": 2, "company": "B", "title": "Senior Dev", "start_date": "2024-06", "end_date": None, "description": "", "match_reasons": [], "included": True, "order": 0},
        {"id": 3, "company": "C", "title": "Mid Dev", "start_date": "2022-03", "end_date": "2024-05", "description": "", "match_reasons": [], "included": True, "order": 0},
    ])

    response = client.post("/api/resumes/generate", json={"job_description": "X" * 150})

    assert response.status_code == 200
    work_experiences = response.json()["resume"]["work_experiences"]
    start_dates = [we["start_date"] for we in work_experiences]
    assert start_dates == ["2024-06", "2022-03", "2020-01"]


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_handles_ongoing_jobs_by_start_date(mock_llm, client):
    _create_minimal_profile(client)

    mock_llm.return_value = _build_llm_result([
        {"id": 1, "company": "Q", "title": "Engineer", "start_date": "2023-06", "end_date": "2024-12", "description": "", "match_reasons": [], "included": True, "order": 0},
        {"id": 2, "company": "P", "title": "Lead", "start_date": "2024-01", "end_date": None, "description": "", "match_reasons": [], "included": True, "order": 0},
    ])

    response = client.post("/api/resumes/generate", json={"job_description": "X" * 150})

    assert response.status_code == 200
    work_experiences = response.json()["resume"]["work_experiences"]
    companies = [we["company"] for we in work_experiences]
    assert companies == ["P", "Q"]


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_handles_two_ongoing_jobs(mock_llm, client):
    _create_minimal_profile(client)

    mock_llm.return_value = _build_llm_result([
        {"id": 1, "company": "R", "title": "Earlier Lead", "start_date": "2024-03", "end_date": None, "description": "", "match_reasons": [], "included": True, "order": 0},
        {"id": 2, "company": "S", "title": "Later Lead", "start_date": "2024-08", "end_date": None, "description": "", "match_reasons": [], "included": True, "order": 0},
    ])

    response = client.post("/api/resumes/generate", json={"job_description": "X" * 150})

    assert response.status_code == 200
    work_experiences = response.json()["resume"]["work_experiences"]
    companies = [we["company"] for we in work_experiences]
    assert companies == ["S", "R"]


def test_llm_prompts_no_relevance_reorder():
    forbidden = "Reorder work experiences by relevance"
    assert forbidden not in SYSTEM_PROMPT
    assert forbidden not in USER_PROMPT_TEMPLATE
