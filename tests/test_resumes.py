import pytest
from unittest.mock import patch, AsyncMock


def test_list_resumes_empty(client):
    """Test listing resumes when none exist."""
    response = client.get("/api/resumes")
    assert response.status_code == 200
    assert response.json() == []


def test_generate_resume_empty_job_description(client):
    """Test generating resume with empty job description."""
    response = client.post("/api/resumes/generate", json={"job_description": ""})
    assert response.status_code == 422


def test_generate_resume_short_job_description(client):
    """Test generating resume with job description under 100 characters."""
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": "Short JD"},
    )
    assert response.status_code == 422


def test_generate_resume_no_profile(client):
    """Test generating resume when user has no work experience."""
    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    assert response.status_code == 400
    assert "work experience" in response.json()["detail"].lower()


def _create_work_experience(client):
    """Helper to create a work experience."""
    return client.post(
        "/api/work-experiences",
        json={
            "company": "Acme Corp",
            "title": "Senior Developer",
            "start_date": "2020-01",
            "description": "Led development team",
        },
    )


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_resume_success(mock_llm, client):
    """Test successful resume generation."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {
            "required_skills": [{"name": "Python", "matched": True}],
            "preferred_skills": [],
        },
        "resume": {
            "summary": "Experienced developer",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Led team",
                    "match_reasons": ["Python"],
                    "included": True,
                    "order": 1,
                }
            ],
            "skills": [{"name": "Python", "matched": True, "included": True}],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "We are looking for a Software Engineer with Python experience. " * 5
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["job_title"] == "Software Engineer"
    assert result["match_score"] == 85.5
    assert result["id"] is not None


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_get_resume_after_generation(mock_llm, client):
    """Test getting a resume by ID after generation."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    response = client.get(f"/api/resumes/{resume_id}")
    assert response.status_code == 200
    assert response.json()["id"] == resume_id


def test_get_resume_not_found(client):
    """Test getting a resume that doesn't exist."""
    response = client.get("/api/resumes/9999")
    assert response.status_code == 404


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_list_resumes_with_history(mock_llm, client):
    """Test listing resumes returns history."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    client.post("/api/resumes/generate", json={"job_description": long_jd})

    response = client.get("/api/resumes")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["job_title"] == "Software Engineer"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_update_resume(mock_llm, client):
    """Test updating a resume."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Original",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Led team",
                    "match_reasons": [],
                    "included": True,
                    "order": 1,
                }
            ],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    update_data = {
        "resume": {
            "summary": "Updated summary",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Updated description",
                    "match_reasons": [],
                    "included": True,
                    "order": 1,
                }
            ],
            "skills": [],
            "education": [],
            "projects": [],
        }
    }

    response = client.put(f"/api/resumes/{resume_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["resume"]["summary"] == "Updated summary"


def test_update_resume_not_found(client):
    """Test updating a resume that doesn't exist."""
    update_data = {
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        }
    }
    response = client.put("/api/resumes/9999", json=update_data)
    assert response.status_code == 404


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_delete_resume(mock_llm, client):
    """Test deleting a resume."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    response = client.delete(f"/api/resumes/{resume_id}")
    assert response.status_code == 204

    response = client.get(f"/api/resumes/{resume_id}")
    assert response.status_code == 404


def test_delete_resume_not_found(client):
    """Test deleting a resume that doesn't exist."""
    response = client.delete("/api/resumes/9999")
    assert response.status_code == 404


def test_get_complete_profile(client):
    """Test getting the complete profile."""
    _create_work_experience(client)

    response = client.get("/api/profile/complete")
    assert response.status_code == 200
    result = response.json()
    assert "personal_info" in result
    assert "work_experiences" in result
    assert "education" in result
    assert "skills" in result
    assert "projects" in result
    assert len(result["work_experiences"]) == 1
